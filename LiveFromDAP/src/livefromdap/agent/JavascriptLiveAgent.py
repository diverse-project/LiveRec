import os
import subprocess
from debugpy.common.messaging import JsonIOStream
from debugpy.common import sockets

from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .BaseLiveAgent import BaseLiveAgent, DebuggeeTerminatedError
from tree_sitter import Language, Parser


class JavaScriptPreprocessor:
    """Take a javascript file and preprocess it to be used by the agent
    This is done by adding module.exports = {function_name: function_name} to the end of the file
    """
    
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.lang = Language(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin","treesitter","javascript.so")), 'javascript')
        self.parser = Parser()
        self.parser.set_language(self.lang)
        with open(self.input_path, "r") as f:
            source = f.read()
        self.tree = self.parser.parse(bytes(source, "utf8"))
        self.extract_function()
        self.add_module_exports()
        
    def extract_function(self):
        self.functions = {}
        query = self.lang.query(
            """
            (function_declaration
                name: (identifier) @function.name
                body: (statement_block) @function.body)
            """
        )
        
        captures = query.captures(self.tree.root_node)
        # The capture is a list of tuples (node, capture)
        # for each function we have to consecutive captures, the first one is the name, the second one is the body
        for i in range(0, len(captures), 2):
            fun_def = captures[i]
            body = captures[i+1]
            if fun_def[1] == "function.name" and body[1] == "function.body": 
                self.functions[fun_def[0].text.decode("utf8")] = int(body[0].children[1].start_point[0])+1
    
    def add_module_exports(self):
        with open(self.input_path, "r") as f:
            source = f.read()
            
        query = self.lang.query(
            """
            (assignment_expression
            left: (
                member_expression
                property: (property_identifier) @exports
            ))
            """
        )
        captures = query.captures(self.tree.root_node)
        if any(c[0].text.decode("utf8") == "exports" for c in captures):
            old = source.split("\n")
            source = "\n".join(old[:captures[0][0].start_point[0]] + old[captures[0][0].end_point[0]+1:])
            
        source += "\nmodule.exports = {" + ",".join([name for name in self.functions.keys()]) + "}"
        
        with open(self.output_path, "w") as f:
            f.write(source)
            
        

class JavascriptLiveAgent(BaseLiveAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dap_adapter_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin", "js-dap", "dapDebugServer.js"))
        self.runner_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner"))
        self.runner_name = "js_runner.js"
        self.runner_path = os.path.abspath(os.path.join(self.runner_directory, self.runner_name))
        
    def start_server(self):
        self.server_process = subprocess.Popen(
            ["node", self.dap_adapter_path, "8123", "127.0.0.1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            restore_signals=False,
            start_new_session=True,
        )
        # wait for the server to be ready
        while True:
            # check if the process returned an error
            if self.server_process.poll() is not None:
                error = self.server_process.stderr.readline()
                # if address already in use
                if b"Error: listen EADDRINUSE: address already in use" in error:
                    # fidn the process that is using the port
                    p = subprocess.Popen(["lsof", "-i", ":8123"], stdout=subprocess.PIPE)
                    p.wait()
                    lsof_output = p.stdout.readlines()
                    pid = lsof_output[-1].split()[1]
                    subprocess.Popen(["kill", pid])
                    self.start_server()
                    return
            output = self.server_process.stdout.readline()
            # wait for : Debug server listening at 127.0.0.1:8123
            if b"Debug server listening" in output:
                break
        self.main_server = sockets.create_client()
        self.main_server.connect(("localhost", 8123))
        self.main_io = JsonIOStream.from_socket(self.main_server)
        self._entry_line = {}
    
    def restart_server(self):
        self.stop_server()
        self.start_server()
    
    
    def stop_server(self):
        """Stop the target program"""
        # Send a stop request
        stop_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "disconnect",
            "arguments": {
                "restart": False,
                "terminateDebuggee": True
            }
        }
        try:
            self.io.write_json(stop_request)
            self.wait("event", "terminated")
            self.io.close()
        except:
            pass
        try:
            self.io = self.main_io
            self.io.write_json(stop_request)
            self.main_io.close()
        except:
            pass
        try:
            self.server_process.kill()
        except:
            pass
         
    def initialize(self):
        """Send data to the agent"""   
        init_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "initialize",
            "arguments": {
                "clientID": 'vscode',
                "clientName": 'Visual Studio Code',
                "adapterID": 'pwa-node',
                "pathFormat": 'path',
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsVariableType": True,
                "supportsVariablePaging": True,
                "supportsRunInTerminalRequest": True,
                "locale": 'en',
                "supportsProgressReporting": True,
                "supportsInvalidatedEvent": True,
                "supportsMemoryReferences": True,
                "supportsArgsCanBeInterpretedByShell": True,
                "supportsMemoryEvent": True,
                "supportsStartDebuggingRequest": True
            }
        }    
            
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "type": 'pwa-node',
                "name": 'Launch Program',
                "outputCapture": 'console',
                "smartStep": True,
                "sourceMaps": True,
                "sourceMapRenames": True,
                "pauseForSourceMap": False,
                "rootPath": self.runner_directory,
                "outFiles": [
                    f"{self.runner_directory}/**/*.js", 
                     "!**/node_modules/**" 
                ],
                "sourceMapPathOverrides": {
                    'webpack:///./~/*': f'{self.runner_directory}/node_modules/*',
                    'webpack:////*': '/*',
                    'webpack://@?:*/?:*/*': f'{self.runner_directory}/*',
                    'webpack://?:*/*': f'{self.runner_directory}/*',
                    'webpack:///([a-z]):/(.+)': '$1:/$2',
                    'meteor://💻app/*': f'{self.runner_directory}/*'
                },
                "enableContentValidation": True,
                "cascadeTerminateToConfigurations": [],
                "__workspaceFolder": self.runner_directory,
                "cwd": self.runner_directory,
                "env": {},
                "envFile": None,
                "localRoot": None,
                "remoteRoot": None,
                "autoAttachChildProcesses": True,
                "program": self.runner_path,
                "stopOnEntry": False,
                "console": 'internalConsole',
                "restart": False,
                "args": [],
                "runtimeExecutable": 'node',
                "runtimeVersion": 'default',
                "runtimeArgs": [],
                "attachSimplePort": None,
                "killBehavior": 'forceful',
            }
        }
        self.io = self.main_io # we need to use the main io to initialize to create the target launch
        self.main_io.write_json(init_request)
        self.configuration_done()
        self.wait("event", "initialized")
        self.main_io.write_json(launch_request)
        debugging = self.wait("request", command="startDebugging")
        self.server = sockets.create_client()
        self.server.connect(("localhost", 8123))
        self.io = JsonIOStream.from_socket(self.server)
        self.io.write_json(init_request)
        self.setup_runner_breakpoint()
        self.io.write_json({
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": debugging["arguments"]["configuration"]
        })
        brk = self.wait("event", "stopped")
        self.thread_id = brk["body"]["threadId"]
    
    def stop_debugee(self):
        terminate_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "disconnect",
            "arguments": {
                "restart": False,
                "terminateDebuggee": True
            }
        }
        self.io.write_json(terminate_request)
        self.server.close()
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [21])
        self.configuration_done()


    def load_code(self, path):
        """For this agent, loading code is loading a class in the runner"""
        jspp = JavaScriptPreprocessor(path, path)
        self._entry_line[path] = jspp.functions
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        self.evaluate(f'loadFile("{path}")', frame_id)


    def execute(self, path, method, args, max_steps=100):
        """Execute a method with the given arguments"""
        if not path in self._entry_line:
            self.load_code(path)
            
        if not method in self._entry_line[path]:
            return
        
        self.set_breakpoint(path, [self._entry_line[path][method]])
        
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        self.evaluate(f"target_function = {method}", frame_id)
        self.evaluate(f"target_args = [{','.join(args)}]", frame_id)
        
        self.next_breakpoint()
        self.wait("event", "stopped")
        # We can now start the stack recording
        stackrecording = StackRecording()
        initial_height = None
        i = 0
        while True:
            stacktrace = self.get_stackframes()
            if initial_height is None:
                initial_height = len(stacktrace)
                height = 0
            else:
                height = len(stacktrace) - initial_height
            print(stacktrace[0]["name"], stacktrace[0]["line"])
            if stacktrace[0]["name"] != method:
                break
            # We need to get local variables
            scope = self.get_scopes(stacktrace[0]["id"])[0]
            variables = self.get_variables(scope["variablesReference"])
            stackframe = Stackframe(stacktrace[0]["line"], stacktrace[0]["column"], height, variables)
            stackrecording.add_stackframe(stackframe)
            i += 1
            if i > max_steps:
                self.restart_server()
                self.initialize()
                return "Interrupted", stackrecording
            self.step()
            try:
                self.wait("event", "stopped")
            except DebuggeeTerminatedError:
                print("Debuggee terminated in execution, restarting")
                self.restart_server()
                self.initialize()
                return "Interrupted", stackrecording
        # We are now out of the function, we need to get the return value
        # Pop the last stackframe
        if len(stackrecording.stackframes) > 1:
            last = stackrecording.stackframes.pop()
            stackrecording.stackframes[-1].set_successor(None)
            return_value = last.get_variable("Return value")
        else:
            return_value = None
        for i in range(2): # Needed to reset the debugger agent loop
            self.next_breakpoint()
            self.wait("event", "stopped")
        return return_value, stackrecording

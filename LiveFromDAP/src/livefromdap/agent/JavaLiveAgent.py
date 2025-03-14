import os
import subprocess
from typing import Any
from debugpy.common.messaging import JsonIOStream # type: ignore
from debugpy.common import sockets # type: ignore

from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .BaseLiveAgent import BaseLiveAgent
from .JavaParams import *

class JavaLiveAgent(BaseLiveAgent):
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) # type: ignore
        self.ls_server_path : str = kwargs.get("ls_server_path", os.path.join(os.path.dirname(__file__), "..", "bin", "jdt-language-server", "bin", "jdtls"))
        assert os.path.exists(self.ls_server_path), f"Could not find language server at {self.ls_server_path}"
        self.debug_jar_path = kwargs.get("debug_jar_path", os.path.join(os.path.dirname(__file__), "..", "bin", "com.microsoft.java.debug.plugin.jar"))
        assert os.path.exists(self.debug_jar_path), f"Could not find debug jar at {self.debug_jar_path}"
        self.runner_path = kwargs.get("runner_path", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner")))
        self.runner_file = kwargs.get("runner_file", "Runner.java")
        assert os.path.exists(os.path.join(self.runner_path, self.runner_file)), f"Could not find runner file at {os.path.join(self.runner_path, self.runner_file)}"
        self.project_name = ""
        self.method_loaded= None
        self.loaded_classes = {}
        self.loaded_class_paths = []
        self.last_args = None

    def start_ls_server(self):
        self.ls_server = subprocess.Popen(
            [self.ls_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.ls_capabilities : list[str] = []
        self.ls_io = JsonIOStream.from_process(self.ls_server)
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
            "processId": self.ls_server.pid,
            "rootPath": self.runner_path,
            "rootUri": f"file://{self.runner_path}",
            "capabilities": LS_INITIALIZE_CAPABILITIES,
            "initializationOptions": {
                "bundles": [
                    os.path.abspath(self.debug_jar_path),
                ],
                "workspaceFolders": [
                    f"file://{self.runner_path}"
                ],
                "settings": LS_INITIALIZE_SETTINGS
            },
            "trace": "verbose",
            "workspaceFolders": [
                {
                    "uri": f"file://{self.runner_path}",
                    "name": "runner"
                }
            ],
        }
        })
        while True:
            response : dict = self.ls_io.read_json() # type: ignore
            if self.debug: print("[LanguageServer]", response)
            if "method" in response and response["method"] == "client/registerCapability" and response["params"]["registrations"][0]["method"] == "workspace/executeCommand":
                self.ls_capabilities += response["params"]["registrations"][0]["registerOptions"]["commands"]
            if "id" in response and response["id"] == 1:
                break
        # Send the initialized notification
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        })
        runner_file_path = os.path.join(self.runner_path, self.runner_file)
        self.lsp_add_document(runner_file_path)
        while True:
            response = self.ls_io.read_json() # type: ignore
            if self.debug: print("[LanguageServer]", response)
            if "method" in response and response["method"] == "client/registerCapability" and response["params"]["registrations"][0]["method"] == "workspace/executeCommand":
                self.ls_capabilities += response["params"]["registrations"][0]["registerOptions"]["commands"]
            if "java.resolvePath" in self.ls_capabilities or "java.reloadBundles" in self.ls_capabilities:
                break
            if "method" in response and response["method"] == "workspace/executeClientCommand" and response["params"]["command"] == "_java.reloadBundles.command":
                break
        
        if "java.resolvePath" in self.ls_capabilities:
            self.ls_io.write_json({
                "jsonrpc": "2.0",
                "id": 30,
                "method": "workspace/executeCommand",
                "params": {
                    "command": "java.resolvePath",
                    "arguments": [
                        f"file://{runner_file_path}",
                    ]
                }
            })
            while True:
                response = self.ls_io.read_json() # type: ignore
                if self.debug: print("[LanguageServer]",response)
                if "id" in response and response["id"] == 30:
                    break
            self.project_name = response["result"][0]["name"]
        elif "java.project.getAll" in self.ls_capabilities and "java.project.getSettings" in self.ls_capabilities:
            self.ls_io.write_json({
                "jsonrpc": "2.0",
                "id": 30,
                "method": "workspace/executeCommand",
                "params": {
                    "command": "java.project.getAll",
                    "arguments": []
                }
            })
        
            while True:
                response = self.ls_io.read_json() # type: ignore
                if self.debug: print("[LanguageServer]",response)
                if "id" in response and response["id"] == 30:
                    break
            self.ls_io.write_json({
                "jsonrpc": "2.0",
                "id": 32,
                "method": "workspace/executeCommand",
                "params": {
                    "command": "java.project.getSettings",
                    "arguments": [
                        response['result'][-1],
                        [
                            "org.eclipse.jdt.ls.core.vm.location",
                            "org.eclipse.jdt.ls.core.outputPath",
                        ]
                    ]
                }
            })
            while True:
                response = self.ls_io.read_json() # type: ignore
                if self.debug: print("[LanguageServer]",response)
                if "id" in response and response["id"] == 32:
                    break
            self.jvm_path = response["result"]["org.eclipse.jdt.ls.core.vm.location"]
            outputPath = response["result"]["org.eclipse.jdt.ls.core.outputPath"]
            self.project_name = outputPath.split("/")[-2]
        
    def lsp_add_document(self, file_path : str):
        with open(file_path, "r") as f:
            file_code = f.read()
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}",
                    "languageId": "java",
                    "version": 1,
                    "text": file_code
                }
            }
        })

    def restart_ls_server(self):
        self.ls_server.kill()
        self.start_ls_server()

    def start_server(self):
        """Create a subprocess with the agent"""
        if not hasattr(self, "ls_server") or self.ls_server is None:
            self.start_ls_server()
        # check if ls server crashed
        if self.ls_server.poll() is not None:
            self.restart_ls_server()
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "workspace/executeCommand",
            "params": {
                "title": "Java: Getting Started",
                "command": "vscode.java.startDebugSession",
                "arguments": []
            }
        })
        debug_serport = None
        while True:
            response : dict = self.ls_io.read_json() # type: ignore
            if self.debug: print("[LanguageServer]", response)
            if "id" in response and response["id"] == 2:
                debug_serport = response["result"]
                break
        
        self.server = sockets.create_client()
        self.server.connect(("localhost", debug_serport))
        self.io = JsonIOStream.from_socket(self.server)
    
    def restart_server(self):
        self.stop_debugee()
        self.start_server()
         
    def initialize(self):
        """Send data to the agent"""
        init_request = init_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "initialize",
            "arguments": {
                "clientID": "vscode",
                "clientName": "Visual Studio Code",
                "adapterID": "java",
                "pathFormat": "path",
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsVariableType": True,
                "supportsVariablePaging": True,
                "supportsRunInTerminalRequest": True,
                "locale": "en",
                "supportsProgressReporting": True,
                "supportsInvalidatedEvent": True,
                "supportMemoryReferences": True,
                "supportsArgsCanBeInterpretedByShell": True,
                "supportsMemoryEvent": True,
                "supportsStartDebuggingRequest": True,
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "type": "java",
                "name": "Launch Current File",
                "request": "launch",
                "cwd": self.runner_path,
                "console": "integratedTerminal",
                "stopOnEntry": False,
                "mainClass": "Runner",
                "args": "",
                "vmArgs": "",
                "env": {},
                "noDebug": False,
                "classPaths": [
                    f"{self.runner_path}/bin",
                    self.runner_path,
                ],
                "projectName": self.project_name,
            }
        }
        self.io.write_json(init_request)
        self.io.write_json(launch_request)
        self.wait("event", "initialized")
        self.setup_runner_breakpoint()
        brk = self.wait("event", "stopped")
        self.thread_id = brk["body"]["threadId"]

    def stop_server(self):
        """Stop the target program"""
        self.stop_debugee()
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "method": "shutdown",
            "params": {}
        })
        self.ls_server.kill()

    
    def stop_debugee(self):
        disconnect_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "disconnect",
            "arguments": {
                "restart": False,
                "terminateDebuggee": True
            }
        }
        self.io.write_json(disconnect_request)
        self.wait("event", "terminated")
        self.server.close()
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(os.path.join(self.runner_path, self.runner_file), [56])
        self.configuration_done()

    def add_classpath(self, classpath):
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        self.evaluate(f"runner.addPath(\"{classpath}\")", frame_id)
        self.loaded_class_paths.append(classpath)
    
    def load_code(self, class_path, class_name):
        """For this agent, loading code is loading a class in the runner"""
        if class_path not in self.loaded_class_paths:
            self.add_classpath(class_path)
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        self.evaluate(f"runner.loadClass(\"{class_name}\")", frame_id)
        target_file = os.path.join(class_path, class_name + ".java")
        if class_name not in self.loaded_classes:
            self.loaded_classes[class_name] = os.path.abspath(os.path.join(class_path, class_name + ".java"))
        self.lsp_add_document(target_file)

    def load_method(self, method_name):
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        self.evaluate(f"runner.loadMethod(\"{method_name}\")", frame_id)
        self.method_loaded = method_name
            
    def get_start_line(self, file_path : str, class_name : str, method_name : str) -> int:
        """Get the first line of the file"""
        seq_id = self.new_seq()
        def_req = {
            "jsonrpc": "2.0",
            "id": seq_id,
            "method": "textDocument/documentSymbol",
            "params": {
                "textDocument": {
                    "uri": f"file://{os.path.abspath(file_path)}"
                }
            }
        }
        self.ls_io.write_json(def_req)
        while True:
            output : dict = self.ls_io.read_json() # type: ignore
            if self.debug: print("[LSP]", output)
            if "id" in output and output["id"] == seq_id:
                break
        classes = output["result"]
        for clazz in classes:
            if clazz["name"] == class_name:
                for method in clazz["children"]:
                    if f"{method_name}(" in method["name"]:
                        return method["range"]["start"]["line"]
        return -1
    
    def get_local_variables(self):
        stacktrace = self.get_stackframes(thread_id=self.thread_id)
        if self.initial_height is None:
            self.initial_height = len(stacktrace)
        height = len(stacktrace) - self.initial_height
        frame_id = stacktrace[0]["id"]
        scope_name,line_number, column = stacktrace[0]["name"], stacktrace[0]["line"], stacktrace[0]["column"]
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variablesReference"])
        for variable in variables:
            if "[]" in variable["type"]:
                value = "["
                sub_variables = self.get_variables(variable["variablesReference"])
                for sub_variable in sub_variables:
                    value += sub_variable["value"] + ","
                if len(value) > 1:
                    value = value[:-1] + "]"
                else:
                    value += "]"
                variable["value"] = value

        return (not self.method_loaded in scope_name), line_number, column, height, variables

    def execute(self, clazz, method, args, max_steps=100, bypass_arg_optim=True):
        """Execute a method with the given arguments"""
        if not clazz in self.loaded_classes.keys(): # error, class not loaded
            raise Exception(f"Class {clazz} not loaded")
        self.load_method(method)

        # Setup function breakpoints
        breakpoint = self.get_start_line(self.loaded_classes[clazz], clazz, method) + 1
        self.set_breakpoint(self.loaded_classes[clazz], [breakpoint])

        if bypass_arg_optim or self.last_args is None or self.last_args != args:
            frame_id = self.get_stackframes(self.thread_id)[0]["id"]
            # We need to load the arguments into the target program
            self.evaluate(f"runner.args = new Object[{len(args)}]", frame_id)
            for i, arg in enumerate(args):
                if arg.startswith('{') and arg.endswith('}'):
                    raise NotImplementedError("Array need to be created, for example replace {'a', 'b'} with new char[]{'a', 'b'}")
                self.evaluate(f"runner.args[{i}] = {arg}", frame_id)
            self.last_args = args

        self.next_breakpoint()
        self.wait("event", "stopped")
        # We can now start the stack recording
        stacktrace = StackRecording()
        self.initial_height = None
        i = 0
        while True:
            stop, line, column, height, variables = self.get_local_variables()
            
            i += 1
            if i > max_steps:
                # we need to pop the current frame
                self.restart_server()
                self.initialize()
                self.loaded_classes = {}
                self.loaded_class_paths = []
                self.last_args = None
                return "Interrupted", stacktrace
            if stop:
                if variables[0]["name"].startswith(f"->{method}"):
                    return_value = variables[0]["value"]
                else:
                    return_value = None
                self.next_breakpoint()
                self.wait("event", event="stopped")
                break
            stackframe = Stackframe(line, column, height, variables)
            stacktrace.add_stackframe(stackframe)
            self.step(thread_id=self.thread_id)
            self.wait("event", event="stopped")
        return return_value, stacktrace

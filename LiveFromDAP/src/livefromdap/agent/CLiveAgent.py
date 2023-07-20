import os
import subprocess
import time
import pycparser
from debugpy.common.messaging import JsonIOStream

from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .BaseLiveAgent import BaseLiveAgent

class FunctionEndFinder(pycparser.c_ast.NodeVisitor):
    """Find the possible end line of a function(return and closing bracket)"""

    def __init__(self, path, function_name):
        self.function_name = function_name
        with open(path, 'r') as file:
            self.code = file.read()
        self.ast = pycparser.parse_file(os.path.abspath(path), use_cpp=True)
        self.end_line = []
        self.visit(self.ast)
        
    def matching_curly_bracket(self, code, start):
        stack = []
        brackets = []
        lines = code.split("\n")
        for i, line in enumerate(lines[start:]):
            for c in line:
                if c == '{':
                    stack.append(i)
                elif c == '}':
                    j = stack.pop()
                    brackets.append((start+j+1, start+i+1))
        return brackets
        
    def visit_FuncDef(self, node):
        if node.decl.name == self.function_name:
            last_line = self.matching_curly_bracket(self.code, node.coord.line-1)[-1][1]
            self.end_line.append(last_line)
            
    def visit_Return(self, node):
        self.end_line.append(node.coord.line)
        self.generic_visit(node)



class CLiveAgent(BaseLiveAgent):
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.compile_command = kwargs.get("compile_command", "gcc -g -fPIC -shared -o {target_input} {target_output}")
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "c_runner.c"))
        self.runner_path_exec = kwargs.pop("runner_path_exec", os.path.join(os.path.dirname(__file__), "..", "runner", "c_runner"))
        self.dap_server_path = kwargs.get("dap_server_path", os.path.join(os.path.dirname(__file__), "..", "bin", "OpenDebugAD7", "OpenDebugAD7"))
        self.current_loaded_shared_libraries = None
        self.main_thread_id = None

    def start_server(self):
        """Create a subprocess with the agent"""
        self.server = subprocess.Popen(
            [self.dap_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.io = JsonIOStream.from_process(self.server)

    def stop_server(self) -> None:
        """Stop the Agent"""
        self.server.kill()
    
    def restart_server(self):
        self.server.kill()
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
                "adapterID": "cppdbg",
                "pathFormat": "path",
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsVariableType": True,
                "supportsVariablePaging": True,
                "supportsRunInTerminalRequest": True,
                "locale": "en",
                "supportsProgressReporting": True,
                "supportsInvalidatedEvent": True,
                "supportsMemoryReferences": True,
                "supportsArgsCanBeInterpretedByShell": True,
                "supportsMemoryEvent": True,
                "supportsStartDebuggingRequest": True,
                "MIMode": "gdb",
                "miDebuggerPath": "/usr/bin/gdb",
                "setupCommands": [
                    {
                        "description": "Enable pretty-printing for gdb",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    }
                ],
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "name": "(gdb) Launch main",
                "type": "cppdbg",
                "request": "launch",
                "program": self.runner_path_exec,
                "args": [],
                "stopAtEntry": False,
                "cwd": os.getcwd(),
                "environment": [],
                "externalConsole": False,
                "MIMode": "gdb",
                "setupCommands": [
                    {
                        "description": "Enable pretty-printing for gdb",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    },
                    {
                        "description": "Set Disassembly Flavor to Intel",
                        "text": "-gdb-set disassembly-flavor intel",
                        "ignoreFailures": True
                    }
                ],
            }
        }
        self.io.write_json(init_request)
        self.io.write_json(launch_request)
        self.wait("event", "initialized")
        self.setup_runner_breakpoint()
        brk = self.wait("event", "stopped")
        self.main_thread_id = brk["body"]["threadId"]

    def compile(self, input_file=None, output_file=None):
        """Compile the target file"""
        compilation = subprocess.run(self.compile_command.format(target_input=input_file, target_output=output_file), shell=True, check=True)
        return compilation.returncode
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [14])
        self.configuration_done()

    def load_code(self, path: str):
        """Load the code to debug,
        compile it if needed"""
        # check if the file is not a shared library
        if not path.endswith(".so"):
            # change the extension to .so
            compiled_path = path[:-2] + ".so"
            # compile the file
            self.compile(input_file=os.path.abspath(path), output_file=os.path.abspath(compiled_path))
            path = compiled_path
        frame_id = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        libname = os.path.basename(path)
        if self.current_loaded_shared_libraries is not None:
            self.evaluate(f"-exec call close_lib()", frame_id)
        self.evaluate(f"-exec call load_lib(\"{path}\")", frame_id)
        self.current_loaded_shared_libraries = libname
            

    def add_variable(self, frame_id, stackframes, stackrecording):
        stackframe = stackframes[0]
        line = stackframe["line"]
        column = stackframe["column"]
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variablesReference"])
        height = len(stackframes) - self.initial_height
        recorded_stackframe = Stackframe(line, column, height, variables)
        stackrecording.add_stackframe(recorded_stackframe)
    
    def execute(self, source_file, method, args, max_steps=300):
        self.set_function_breakpoint([method])
        command = f"-exec call {method}({','.join(args)})"
        frame_id = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        self.evaluate(command, frame_id)
        self.wait("event", event="stopped")
        end_lines = FunctionEndFinder(os.path.abspath(source_file),method).end_line
        stackrecording = StackRecording()
        self.initial_height = None
        i = 0
        while True:
            stackframes = self.get_stackframes(thread_id=self.main_thread_id)
            if self.initial_height is None:
                self.initial_height = len(stackframes)
            frame_id = stackframes[0]["id"]
            if stackframes[0]["name"] == "main()":
                return_value = None
                scope = self.get_scopes(stackframes[0]["id"])[0]
                variables = self.get_variables(scope["variablesReference"])
                if len(variables) == 0:
                    return_value = None
                else:
                    return_value = variables[0]["value"]
                break

            self.add_variable(frame_id, stackframes, stackrecording)
            i += 1
            if i > max_steps:
                self.restart_server()
                self.initialize()
                self.current_loaded_shared_libraries = None
                return "Interrupted", stackrecording
            if stackframes[0]["line"] in end_lines:
                self.evaluate("-exec fin", frame_id)
                self.wait("event", event="stopped")
            else:
                self.step(thread_id=self.main_thread_id)
                self.wait("event", event="stopped")
        return return_value, stackrecording

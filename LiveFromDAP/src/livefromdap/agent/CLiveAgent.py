import os
import subprocess
import time
from debugpy.common.messaging import JsonIOStream

from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .BaseLiveAgent import BaseLiveAgent

class CLiveAgent(BaseLiveAgent):
    def __init__(self, target_file : str, target_methods : list[str] = [], auto_compile : bool = True,**kwargs):
        super().__init__()
        self.target_file = target_file
        self.target_methods = target_methods
        self.auto_compile = auto_compile
        if auto_compile:
            self.target_file_exec = kwargs.get("target_file_exec", f"{self.target_file[:self.target_file.rfind('.')]}.so")
            self.compile_command = kwargs.get("compile_command", f"gcc -g -fPIC -shared -o {self.target_file_exec} {self.target_file}")
        else:
            self.target_file_exec = kwargs.get("target_file_exec", None)
            if not self.target_file_exec:
                raise ValueError("target_file_exec must be specified if auto_compile is False")
            self.compile_command = kwargs.get("compile_command", f"gcc -g -fPIC -shared -o {self.target_file_exec} {self.target_file}")
        
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "c_runner.c"))
        self.runner_path_exec = kwargs.pop("runner_path_exec", os.path.join(os.path.dirname(__file__), "..", "runner", "c_runner"))
        self.is_shared_lib_loaded = False
        self.target_exit_lines = []

    def start_server(self):
        """Create a subprocess with the agent"""
        opendegugad7_path = os.path.join(os.path.dirname(__file__), "..", "bin", "OpenDebugAD7", "OpenDebugAD7")
        self.server = subprocess.Popen(
            [opendegugad7_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.io = JsonIOStream.from_process(self.server)
    
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
        self._setup_breakpoint()
        brk = self.wait("event", "stopped")
        self.thread_id = brk["body"]["threadId"]

    def compile(self):
        """Compile the target file"""
        compilation = subprocess.run(self.compile_command, shell=True, check=True)
        #return the return code of the compilation
        return compilation.returncode
    
    def _setup_breakpoint(self):
        self.set_breakpoint(self.runner_path, [14])
        self.set_function_breakpoint(self.target_methods)
        self.configuration_done()

    def set_target_methods(self, methods):
        self.target_methods = methods
        self.set_function_breakpoint(self.target_methods)

    def find_return(self):
        self.return_line = [] # TODO : find function end when no return
        with open(self.target_file, "r") as f:
            for i,line in enumerate(f):
                if "return" in line:
                    self.return_line.append(i+1)

    def load_code(self):
        if self.auto_compile:
            self.compile()
        frame_id = self.get_stackframes(thread_id=self.thread_id)[0]["id"]
        if self.is_shared_lib_loaded:
            self.evaluate(f"-exec call close_lib()", frame_id=frame_id)
        self.evaluate(f"-exec call load_lib(\"{self.target_file_exec}\")", frame_id=frame_id)
        self.is_shared_lib_loaded = True
        self.find_return()
            

    def evaluate(self, expression, frame_id):
        evaluate_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "evaluate",
            "arguments": {
                "expression": expression,
                "frameId": frame_id,
            }
        }
        self.io.write_json(evaluate_request)
        self.wait("response", command="evaluate")


    def get_local_variables(self):
        stacktrace = self.get_stackframes(thread_id=self.thread_id)
        frame_id = stacktrace[0]["id"]
        _,line_number = stacktrace[0]["source"]["name"], stacktrace[0]["line"]
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variablesReference"])
        return int(line_number) in self.return_line, line_number, variables
    
    def execute(self, method, args):
        if not method in self.target_methods:
            self.set_target_methods([method])
        command = f"-exec call {method}({','.join(args)})"
        frame_id = self.get_stackframes(thread_id=self.thread_id)[0]["id"]
        self.evaluate(command, frame_id=frame_id)
        self.wait("event", event="stopped")
        stacktrace = StackRecording()
        while True:
            stop, line, variables = self.get_local_variables()
            stackframe = Stackframe(line, variables)
            stacktrace.add_stackframe(stackframe)
            if stop:
                self.step_out(thread_id=self.thread_id)
                self.wait("event", event="stopped")
                _, _, variables = self.get_local_variables()
                return_value = variables[0]
                break
            self.step(thread_id=self.thread_id)
            self.wait("event", event="stopped")
        return return_value, stacktrace

import os
import subprocess
import time

from livefromdap.utils.StackRecord import Stackframe, StackRecord
from .BaseLiveAgent import BaseLiveAgent

class CLiveAgent(BaseLiveAgent):

    def __init__(self, *args, **kwargs):
        self.runner_path_exec = kwargs.pop("runner_path_exec")
        self.target_path_exec = kwargs.pop("target_path_exec")
        self.loaded_coder = False
        self.return_line = []
        super().__init__(*args, **kwargs)
        self.init()
        self.wait("event", "initialized")
        self.setup_breakpoint()
        brk = self.wait("event", "stopped")
        self.thread_id = brk["body"]["threadId"]

    def create_job(self) -> subprocess.Popen:
        """Create a subprocess with the agent"""
        opendegugad7_path = os.path.join(os.path.dirname(__file__), "..", "bin", "OpenDebugAD7", "OpenDebugAD7")
        return subprocess.Popen(
            [opendegugad7_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    def init(self):
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

    def setup_breakpoint(self):
        self._set_breakpoint(self.runner_path, [14])
        self._set_function_breakpoint([self.target_method])
        
        complete_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "configurationDone"
        }
        self.io.write_json(complete_request)

    def set_target_method(self, method):
        self.target_method = method
        self._set_function_breakpoint([self.target_method])

    def _load_code(self):
        frame_id = self.get_stackframes(thread_id=self.thread_id)[0]["id"]
        self.evaluate(f"-exec call load_lib(\"{self.target_path_exec}\")", frame_id=frame_id)
        self.wait("response", command="evaluate")
        self.find_return()
        self.loaded_coder = True

    def find_return(self):
        self.return_line = []
        with open(self.target_path, "r") as f:
            for i,line in enumerate(f):
                if "return" in line:
                    self.return_line.append(i+1)

    def load_code(self):
        print("the live agent load code")
        if self.loaded_coder:
            frame_id = self.get_stackframes(thread_id=self.thread_id)[0]["id"]
            self.evaluate(f"-exec call close_lib()", frame_id=frame_id)
            self.wait("response", command="evaluate")
            self._load_code()
        else:
            self._load_code()

    def evaluate(self, expression, frame_id):
        evaluate_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "evaluate",
            "arguments": {
                "expression": expression,
            }
        }
        if frame_id:
            evaluate_request["arguments"]["frameId"] = frame_id
        self.io.write_json(evaluate_request)


    def get_local_variables(self):
        stacktrace = self.get_stackframes(thread_id=self.thread_id)
        frame_id = stacktrace[0]["id"]
        _,line_number = stacktrace[0]["source"]["name"], stacktrace[0]["line"]
        
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variablesReference"])

        return int(line_number) in self.return_line, line_number, variables
    
    def jump(self, location):
        self.evaluate(f"-exec jump {location}", frame_id=self.get_stackframes(thread_id=self.thread_id)[0]["id"])
        self.wait("event", event="stopped")

    def execute(self, args):
        self.find_return()
        command = f"-exec call {self.target_method}({','.join(args)})"
        frame_id = self.get_stackframes(thread_id=self.thread_id)[0]["id"]
        self.evaluate(command, frame_id=frame_id)
        self.wait("event", event="stopped")
        stacktrace = StackRecord()
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

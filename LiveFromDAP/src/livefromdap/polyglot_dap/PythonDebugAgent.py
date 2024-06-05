import os
import subprocess
import sys
import time
from typing import override

import debugpy
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseDebugAgent import BaseDebugAgent


class PythonDebugAgent(BaseDebugAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "py_runner.py"))
        self.debugpy_adapter_path = kwargs.get("debugpy_adapter_path", os.path.join(os.path.dirname(debugpy.__file__), "adapter"))
        # self.debug = True

    def start_server(self):
        """Create a subprocess with the agent"""
        self.server = subprocess.Popen(
            ["python", self.debugpy_adapter_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            restore_signals=False,
            start_new_session=True,
        )

        self.io = JsonIOStream.from_process(self.server)
    
    def restart_server(self):
        self.server.kill()
        self.start_server()

    def stop_server(self):
        """Kill the subprocess"""
        self.server.kill()
        if getattr(self, "debugee", None) is not None:
            self.debugee.kill()
    
    def initialize(self):
        """Send data to the agent"""
        init_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "initialize",
            "arguments": {
                "clientID": "vscode",
                "clientName": "Visual Studio Code",
                "adapterID": "python",
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
                "supportsStartDebuggingRequest": True
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "name": f"Debug Python agent live",
                "type": "python",
                "request": "launch",
                "program": self.runner_path,
                "console": "internalConsole",
                # get the current python interpreter
                "python": sys.executable,
                "debugAdapterPython": sys.executable,
                "debugLauncherPython": sys.executable,
                "clientOS": "unix",
                "cwd": os.getcwd(),
                "envFile": os.path.join(os.getcwd(), ".env"),
                "env": {
                    "PYTHONIOENCODING": "UTF-8",
                    "PYTHONUNBUFFERED": "1"
                },
                # stop debug on entry to allow DAP manipulation
                "stopOnEntry": True, 
                "showReturnValue": True,
                "internalConsoleOptions": "neverOpen",
                "debugOptions": [
                    "ShowReturnValue"
                ],
                "justMyCode": False,
                "workspaceFolder": os.getcwd(),
            }
        }
        self.io.write_json(init_request)
        self.io.write_json(launch_request)
        self.wait("event", "initialized")
        self.setup_runner_breakpoint()
        # self.wait("event", "stopped")
        return 5
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [26,39])
        self.set_function_breakpoint(["polyglotEval"])
        self.configuration_done()
        
    
    def load_code(self, path: str):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_import('{os.path.abspath(path)}')", frameId)
        self.next_breakpoint()
    


    def execute(self, filePath):
        stackframe = self.get_stackframes()[0]
        print(stackframe)
        # self.set_breakpoint(os.path.join(os.path.dirname(__file__), "..", "runner", "test.py"), [3])
        # self.set_breakpoint(os.path.join(os.path.dirname(__file__), "..", "runner", "test2.py"), [1])
        self.next_breakpoint()
        stackframe = self.get_stackframes()[0]
        print(stackframe)
        self.load_code(filePath)
        stackframe = self.get_stackframes()[0]
        if stackframe["source"]["path"] == "/code/src/livefromdap/runner/py_runner.py":
            if stackframe["name"] == "<module>" and stackframe["line"] == 39:
                # runner was on standby, we just need to load the code and resume execution
                self.load_code(filePath)
                self.next_breakpoint()
      
            elif stackframe["name"] == "polyglotEval" and stackframe["line"] == 19:
                frameId = self.get_stackframes()[0]["id"]
                self.evaluate(f"src_file = '{filePath}'", frameId)
                self.next_breakpoint()
            
        print(stackframe)
        # print("while loop:", self.get_stackframes()[0])
        # self.load_code(os.path.join(os.path.dirname(__file__), "..", "runner", "test.py"))
        # print("normal breakpoint:", self.get_stackframes()[0])
        # self.next_breakpoint()
        # print("polyglot breakpoint:", self.get_stackframes()[0])
        # self.step()
        # self.step()
        # print("inside polyg:", self.get_stackframes()[0])
        # frameId = self.get_stackframes()[0]["id"]
        # print(self.evaluate(f"src_file = '{os.path.join(os.path.dirname(__file__), "..", "runner", "test2.py")}'", frameId))
        # self.next_breakpoint()
        # print("inside test2:", self.get_stackframes()[0])
        # self.next_breakpoint()
        # print("peekaboo:", self.get_stackframes()[0])
        # frameId = self.get_stackframes()[0]["id"]
        # print(self.evaluate("intermediate_ret", frameId))
        # self.next_breakpoint()
        # print("while loop again:", self.get_stackframes()[0])
        # frameId = self.get_stackframes()[0]["id"]
        
        return "execution reached!"
    
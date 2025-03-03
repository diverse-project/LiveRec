import json
import os
import subprocess
import sys
from typing import Any

import debugpy
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseLiveAgent import BaseLiveAgent


class AdvancedPythonLiveAgent(BaseLiveAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "advanced_py_runner.py"))
        self.debugpy_adapter_path = kwargs.get("debugpy_adapter_path", os.path.join(os.path.dirname(debugpy.__file__), "adapter"))
        self.tracked_functions = []
        self.mocked_functions = {}

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
                "stopOnEntry": False,
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
        self.wait("event", "stopped")
        return 5
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [147])
        self.configuration_done()
    
    def load_code(self):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_reload_code(True)", frameId)
        self.next_breakpoint()
        self.wait("event", "stopped")

    def set_source_path(self, path: str):
        self.source_path = path
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_source_path('{os.path.abspath(path)}')", frameId)
        self.next_breakpoint()
        self.wait("event", "stopped")

    def get_clean_name(self, function : str):
        return function.split(".")[-1].strip()

    def start_execution(self, method : str, data_dict : str):
        if method not in self.tracked_functions:
            self.track_function(method)
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        print("Executing", method, data_dict)
        self.evaluate(f"load_data('{method}', '{data_dict}')", frameId)
        # We need to run the debug agent loop until we are on a breakpoint in the target method
        
        i = 0
        while True:
            stacktrace = self.get_stackframes()
            if stacktrace[0]["name"] == self.get_clean_name(method):
                break
            self.next_breakpoint()
            self.wait("event", "stopped")
            i += 1
            if i > 5: # Maybe code was not loaded
                print("Failed to find breakpoint in", method)
                return False
        return True

    def track_function(self, function : str):
        function = self.get_clean_name(function)
        if function not in self.tracked_functions:
            self.tracked_functions.append(function)
            self.set_function_breakpoint(self.tracked_functions)
            self.wait("response", command="setFunctionBreakpoints")

    def add_mocked_data(self, path : str):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"add_mocked_data('{path}')", frameId)
        self.next_breakpoint()
        self.wait("event", "stopped")

        
    def execute(self, method : str, args : dict, max_steps=300) -> tuple[Any, StackRecording]:
        stackrecording = StackRecording()
        if not self.start_execution(method, args):
            return "Interrupted", stackrecording
        # We are now in the function, we need to get all information, step, and check if we are still in the function
        scope = None
        initial_height = None
        i = 0
        stacktrace = self.get_stackframes()
        while True:
            stacktrace = self.get_stackframes()

            if stacktrace[0]["name"] in self.tracked_functions:

                # We are in a tracked function, we need to get the return value
                if initial_height is None:
                    initial_height = len(stacktrace)
                    height = 0
                else:
                    height = len(stacktrace) - initial_height
                if not scope:
                    scope = self.get_scopes(stacktrace[0]["id"])[0]
                variables = self.get_variables(scope["variablesReference"])
                stackframe = Stackframe(stacktrace[0]["line"], stacktrace[0]["column"], height, variables)
                stackrecording.add_stackframe(stackframe)
                self.step()
            
            
                i += 1
                if i > max_steps:
                    self.restart_server()
                    self.initialize()
                    return "Interrupted", stackrecording
            else:
                break
            

        # We are now out of the function, we need to get the return value
        scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])
        if variables is None:
            return None, stackrecording
        return_value = None
        for variable in variables:
            if variable["name"].startswith("(return) "):
                return_value = variable["value"]
                break
        for i in range(2): # Needed to reset the debugger agent loop
            self.next_breakpoint()
            self.wait("event", "stopped")
        return return_value, stackrecording
    
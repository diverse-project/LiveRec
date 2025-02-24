import os
import subprocess
import sys

import debugpy
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseLiveAgent import BaseLiveAgent


class PythonLiveAgent(BaseLiveAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "py_runner.py"))
        self.debugpy_adapter_path = kwargs.get("debugpy_adapter_path", os.path.join(os.path.dirname(debugpy.__file__), "adapter"))

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
        self.set_breakpoint(self.runner_path, [7,20])
        # self.set_function_breakpoint(["polyglotEval"])
        self.configuration_done()
    
    def load_code(self, path: str):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_import('{os.path.abspath(path)}')", frameId)
        self.next_breakpoint()
        self.wait("event", "stopped")
            
    def execute(self, method, args, probes, max_steps=50):
        self.set_function_breakpoint([method])
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_method('{method}',[{','.join(args)}])", frameId)
        # We need to run the debug agent loop until we are on a breakpoint in the target method
        stackrecording = StackRecording()
        while True:
            stacktrace = self.get_stackframes()
            if stacktrace[0]["name"] == method:
                break
            self.next_breakpoint()
            self.wait("event", "stopped")
        # We are now in the function, we need to get all information, step, and check if we are still in the function
        scope = None
        initial_height = None
        i = 0
        probe_lines = []
        probe_expressions = []
        for probe in probes:
            probe_lines.append(probe["line"]) # TODO: support multiple files
            probe_expressions.append(probe["expr"])

        ######## TODO: refactor out
        stacktrace = self.get_stackframes()
        if not scope:
            scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])            
        stackframe = Stackframe(stacktrace[0]["line"], stacktrace[0]["column"], 0, variables)
        stackrecording.add_stackframe(stackframe)  
        ########  
        while True:
            stacktrace = self.get_stackframes()
            current_line = stacktrace[0]['line']
            if initial_height is None:
                initial_height = len(stacktrace)
                height = 0
            else:
                height = len(stacktrace) - initial_height
            if stacktrace[0]["name"] != method:
                break
            # We need to get local variables
            if current_line+1 not in probe_lines:
                self.step()
                continue
            self.step()
            if not scope:
                scope = self.get_scopes(stacktrace[0]["id"])[0]
            variables = self.get_variables(scope["variablesReference"])
            probed_variables = []
            for v in variables:
                if v["name"] in probe_expressions:
                    probed_variables.append(v)
                print(v)
            stackframe = Stackframe(stacktrace[0]["line"], stacktrace[0]["column"], height, probed_variables)
            stackrecording.add_stackframe(stackframe)
            i += 1
            if i > max_steps:
                # we need to pop the current frame
                self.restart_server()
                self.initialize()
                return "Interrupted", stackrecording
            # self.step()
        # We are now out of the function, we need to get the return value
        scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])
        return_value = None
        for variable in variables:
            if variable["name"] == f'(return) {method}':
                return_value = variable["value"]
        for i in range(2): # Needed to reset the debugger agent loop
            self.next_breakpoint()
            self.wait("event", "stopped")
        return return_value, stackrecording
    
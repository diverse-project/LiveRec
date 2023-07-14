import os
import subprocess

from livefromdap.utils.StackRecording import StackRecording, Stackframe
from .BaseLiveAgent import BaseLiveAgent
import debugpy
from debugpy.common.messaging import JsonIOStream

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
                "python": "/bin/python",
                "debugAdapterPython": "/bin/python",
                "debugLauncherPython": "/bin/python",
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
        self.set_breakpoint(self.runner_path, [16])
        self.configuration_done()
    
    def load_code(self, path: str):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_import('{os.path.abspath(path)}')", frame_id=frameId)
        self.next_breakpoint()
        self.wait("event", "stopped")
            
    def execute(self, method, args):
        self.set_function_breakpoint([method])
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_method('{method}',[{','.join(args)}])", frame_id=frameId)
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
        while True:
            stacktrace = self.get_stackframes()
            if stacktrace[0]["name"] != method:
                break
            # We need to get local variables
            if not scope:
                scope = self.get_scopes(stacktrace[0]["id"])[0]
            variables = self.get_variables(scope["variablesReference"])
            stackframe = Stackframe(stacktrace[0]["line"], variables)
            stackrecording.add_stackframe(stackframe)
            self.step()
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
    
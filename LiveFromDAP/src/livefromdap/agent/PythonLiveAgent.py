import os
import subprocess

from livefromdap.utils.StackRecording import StackRecording, Stackframe
from .BaseLiveAgent import BaseLiveAgent
import debugpy
from debugpy.common.messaging import JsonIOStream

class PythonLiveAgent(BaseLiveAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""
    def __init__(self, target_path, target_method, **kwargs):
        super().__init__(**kwargs)
        self.target_path = target_path
        self.target_method = target_method
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "py_runner.py"))

    def start_server(self):
        """Create a subprocess with the agent"""
        debugpy_adapter_path = os.path.join(os.path.dirname(debugpy.__file__), "adapter")
        self.server = subprocess.Popen(
            ["python", debugpy_adapter_path],
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
                "console": "integratedTerminal",
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
        self._setup_breakpoint()
        self.wait("event", "stopped")
        print("Agent initialized")
    
    def _setup_breakpoint(self):
        self.set_breakpoint(self.runner_path, [30])
        #self._set_breakpoint(self.target_path, [1, 2]) #TODO: get line number of method
        self.set_function_breakpoint([self.target_method])
        self.configuration_done()
    
    def load_code(self):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_import('{self.target_path}', '{self.target_method}')", frame_id=frameId)
        # We need to run the debug agent loop until method is loaded (and at least 3 times to be sure)
        i = 0
        method_loaded = True
        while i < 3 or not method_loaded:
            # Get the value of method variable
            scope = self.get_scopes(frameId)[0]
            variables = self.get_variables(scope["variablesReference"])
            for variable in variables:
                if variable["name"] == 'method' and variable["value"] != 'None':
                    method_loaded = True
            self.next_breakpoint()
            self.wait("event", "stopped")
            i += 1
            
    def evaluate(self, expression, frame_id=None):
        evaluate_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "evaluate",
            "arguments": {
                "expression": expression,
                "context": "repl"
            }
        }
        if frame_id:
            evaluate_request["arguments"]["frameId"] = frame_id
        self.io.write_json(evaluate_request)
        self.wait("response", command="evaluate")

    def execute(self, method, args):
        if method != self.target_method:
            self.target_method = method
            self.set_function_breakpoint([self.target_method])
            self.load_code()
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_method([{','.join(args)}])", frame_id=frameId)
        # We need to run the debug agent loop until we are on a breakpoint in the target method
        stackrecording = StackRecording()
        while True:
            stacktrace = self.get_stackframes()
            if stacktrace[0]["name"] == self.target_method:
                break
            self.next_breakpoint()
            self.wait("event", "stopped")
        # We are now in the function, we need to get all information, step, and check if we are still in the function
        scope = None
        while True:
            stacktrace = self.get_stackframes()
            if stacktrace[0]["name"] != self.target_method:
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
            if variable["name"] == f'(return) {self.target_method}':
                return_value = variable["value"]
        for i in range(2): # Needed to reset the debugger agent loop
            self.next_breakpoint()
            self.wait("event", "stopped")
        return return_value, stackrecording
    
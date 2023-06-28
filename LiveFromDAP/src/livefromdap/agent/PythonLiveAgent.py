import os
import subprocess
from .BaseLiveAgent import BaseLiveAgent
import debugpy

class PythonLiveAgent(BaseLiveAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method = self.target_method
        self.init()
        self.wait("event", "initialized")
        self.setup_breakpoint()
        self.wait("event", "stopped")

    def create_job(self) -> subprocess.Popen:
        """Create a subprocess with the agent"""
        # find the path to the current debugpy module
        debugpy_adapter_path = os.path.join(os.path.dirname(debugpy.__file__), "adapter")
        return subprocess.Popen(
            ["python", debugpy_adapter_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    def init(self):
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
                "name": f"Debug {self.target_path}.{self.method}",
                "type": "python",
                "request": "launch",
                "program": os.path.join(os.getcwd(), self.runner_path),
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
    
    def setup_breakpoint(self):
        self._set_breakpoint(self.runner_path, [30])
        self._set_breakpoint(self.target_path, [1, 2]) #TODO: get line number of method
        self._set_function_breakpoint([self.method])
        
        complete_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "configurationDone"
        }
        self.io.write_json(complete_request)
    
    def load_code(self):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_import('{self.target_path}', '{self.method}')", frame_id=frameId)
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
            self._continue()
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

    def execute(self, args):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_method([{','.join(args)}])", frame_id=frameId)
        # We need to run the debug agent loop until we are on a breakpoint in the target method
        stackframes = []
        while True:
            stacktrace = self.get_stackframes()
            if stacktrace[0]["name"] == self.method:
                break
            self._continue()
            self.wait("event", "stopped")
        # We are now in the function, we need to get all information, step, and check if we are still in the function
        scope = None
        while True:
            stacktrace = self.get_stackframes()
            if stacktrace[0]["name"] != self.method:
                break
            # We need to get local variables
            if not scope:
                scope = self.get_scopes(stacktrace[0]["id"])[0]
            variables = self.get_variables(scope["variablesReference"])
            stackframes.append({
                "line": stacktrace[0]["line"],
                "variables": variables
            })
            self.step()
        # We are now out of the function, we need to get the return value
        scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])
        return_value = None
        for variable in variables:
            if variable["name"] == f'(return) {self.method}':
                return_value = variable["value"]
        for i in range(2): # Needed to reset the debugger agent loop
            self._continue()
            self.wait("event", "stopped")
        return return_value, stackframes
    
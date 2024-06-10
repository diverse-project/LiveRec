import os
import subprocess

from debugpy.common.messaging import JsonIOStream
from debugpy.common import sockets
from .BaseLiveAgent import BaseLiveAgent
from livefromdap.utils.StackRecording import Stackframe, StackRecording


class GoLangLiveAgent(BaseLiveAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = True
        self.runner_path = kwargs.get("runner_path",
                                      os.path.join(os.path.dirname(__file__), "..", "runner", "golang_runner.go"))

    def start_server(self):
        client_host = "127.0.0.1"  # Replace with actual client host
        client_port = "9000"      # Replace with actual client port

        # Command to start the Delve DAP server
        command = [
            "dlv", "dap",
            "--client-addr", f"{client_host}:{client_port}",
            "--log"
        ]
        self.main_server = sockets.create_client()
        self.main_server.connect(("localhost", 9000))
        self.main_io = JsonIOStream.from_socket(self.main_server)

        # Start the Delve server
        self.server_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    def stop_server(self):
        self.stop_debugee()
        self.server.kill()

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
        self.server.close()

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
                "adapterID": "go",
                "locale": "en",
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "pathFormat": "path",
                "supportsVariableType": True,
                "supportsVariablePaging": True,
                "supportsRunInTerminalRequest": True,
                "supportsMemoryReferences": True,
                "supportsProgressReporting": True,
                "supportsInvalidatedEvent": True,
                "supportsMemoryEvent": True,
                "supportsArgsCanBeInterpretedByShell": True,
                "supportsStartDebuggingRequest": True
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "noDebug": True,
                "name": "Launch"
            }
        }
        # self.io = self.main_io # we need to use the main io to initialize to create the target launch
        # self.main_io.write_json(init_request)
        # self.wait("event", "initialized")
        # self.main_io.write_json(launch_request)
        # debugging = self.wait("request", command="startDebugging")
        # self.server = sockets.create_client()
        # self.server.connect(("localhost", 9000))
        # self.io = JsonIOStream.from_socket(self.server)

    def load_code(self, *args, **kwargs) -> None:
        pass

    def execute(self, method, args, max_steps=50):
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
        while True:
            stacktrace = self.get_stackframes()
            if initial_height is None:
                initial_height = len(stacktrace)
                height = 0
            else:
                height = len(stacktrace) - initial_height
            if stacktrace[0]["name"] != method:
                break
            # We need to get local variables
            if not scope:
                scope = self.get_scopes(stacktrace[0]["id"])[0]
            variables = self.get_variables(scope["variablesReference"])
            stackframe = Stackframe(stacktrace[0]["line"], stacktrace[0]["column"], height, variables)
            stackrecording.add_stackframe(stackframe)
            i += 1
            if i > max_steps:
                # we need to pop the current frame
                self.restart_server()
                self.initialize()
                return "Interrupted", stackrecording
            self.step()
        # We are now out of the function, we need to get the return value
        scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])
        return_value = None
        for variable in variables:
            if variable["name"] == f'(return) {method}':
                return_value = variable["value"]
        for i in range(2):  # Needed to reset the debugger agent loop
            self.next_breakpoint()
            self.wait("event", "stopped")
        return return_value, stackrecording

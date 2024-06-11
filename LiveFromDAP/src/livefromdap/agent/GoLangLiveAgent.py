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
        # Command to start the Delve DAP server
        command = [
            "dlv", "dap",
            "--listen=:9000",
            "--log",
            "--log-output=dap"
        ]
        # Start the Delve server
        self.server_process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            restore_signals=False,
            start_new_session=True,
        )

        # wait for the server to be ready
        while True:
            # check if the process returned an error
            if self.server_process.poll() is not None:
                error = self.server_process.stderr.readline() # type: ignore
                # if address already in use
                if b"Error: listen EADDRINUSE: address already in use" in error:
                    # fidn the process that is using the port
                    p = subprocess.Popen(["lsof", "-i", ":9000"], stdout=subprocess.PIPE)
                    p.wait()
                    lsof_output = p.stdout.readlines() # type: ignore
                    pid = lsof_output[-1].split()[1]
                    subprocess.Popen(["kill", pid])
                    self.start_server()
                    return
            output = self.server_process.stdout.readline() # type: ignore
            # wait for : DAP server listening at: [::]:9000
            if b"DAP server listening at" in output:
                break

        self.main_server = sockets.create_client()
        self.main_server.connect(("localhost", 9000))
        self.main_io = JsonIOStream.from_socket(self.main_server)

    def stop_server(self):
        self.stop_debugee()
        try:
            self.io.close()
        except:
            pass
        try:
            self.io = self.main_io
            self.main_io.close()
        except:
            pass
        try:
            self.server_process.kill()
        except:
            pass

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
        self.wait("response", command="disconnect")
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
                "name": "Launch",
                "program": self.runner_path
            }
        }
        self.io = self.main_io # we need to use the main io to initialize to create the target launch
        self.main_io.write_json(init_request)
        self.wait("response", command="initialize")
        self.main_io.write_json(launch_request)
        debugging = self.wait("response", command="launch")
        self.server = sockets.create_client()
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

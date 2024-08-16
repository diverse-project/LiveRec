import os
import subprocess
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .BaseLiveAgent import BaseLiveAgent


class KotlinLiveAgent(BaseLiveAgent):

    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "kotlin_runner.kt"))
        self.runner_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner"))
        self.dap_server = kwargs.get("dap_server", os.path.join(os.path.dirname(__file__), "..", "bin", "kotlin-debug-adapter", "adapter", "build", "install", "adapter", "bin", "kotlin-debug-adapter"))

        self.thread_id = 1

    #	TODO: add required local params

    def start_server(self):
        #"""Create a subprocess with the agent"""
        #Start server accordingly
        self.server = subprocess.Popen(
            [self.dap_server],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self.io = JsonIOStream.from_process(self.server)

    def stop_server(self) -> None:
        #"""Stop the Agent"""
        #	TODO: add more command to stop dap if needed
        self.server.kill()

    def restart_server(self):
        self.server.kill()
        self.start_server()

    def initialize(self):
        #"""Send data to the agent"""
        init_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "initialize",
            "arguments": {
                "clientID": "vscode",
                "clientName": "Visual Studio Code",
                "adapterID": "kotlin",
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
            }
        }

        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "type": "kotlin",
                "request": "launch",
                "mainClass": "kotlin_runnerKt",
                "projectRoot": self.runner_directory
            }
        }

        self.io.write_json(init_request)
        self.io.write_json(launch_request)
        self.wait("event", "initialized")
        self.setup_runner_breakpoint()
        self.wait("event", "stopped")



    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [84])
        self.configuration_done()

    def load_code(self, path: str):
        #	TODO: Depending on the runner file or the language itself, there will be specific ways
        #		  to load the code, modify method if needed.

        frame_id = self.get_stackframes(thread_id=self.thread_id)["0"]["id"]
        self.evaluate(f"", frame_id)

    def add_variable(self, frame_id, stackframes, stackrecording):
        stackframe = stackframes[0]
        line = stackframe["line"]
        column = stackframe["column"]
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variableReference"])
        height = len(stackframes) - self.initial_height
        recorded_stackframe = Stackframe(line, column, height, variables)
        stackrecording.add_stackframe(recorded_stackframe)

    def execute(self, source_file : str, method : str, args : list[str], max_steps : int=300) -> tuple[str, StackRecording]:
        #	TODO: Arrange order of events and modify method header accordingly.
        self.set_function_breakpoint([method])
        command = f""
        frame_id = self.get_stackframes(thread_id=self.thread_id)[0]["id"]
        self.evaluate(command, frame_id)
        self.wait("event", event="stopped")

        stackrecording = StackRecording()
        return_value = ""
        self.initial_height = -1
        i = 0
        while True:

            #TODO: 1. get the length of the stackframes to set height in the recorded stackframes
            # 	   2. check if we return to the main method if we did then we have the return value

            #								EXAMPLE OF CLiveAgent

            stackframes = self.get_stackframes(thread_id=self.thread_id)
            #if self.initial_height == -1:
            #    self.initial_height = len(stackframes)
            #frame_id = stackframes[0]["id"]
            #if stackframes[0]["name"] == "main()":
            #    return_value = None
            #    scope = self.get_scopes(stackframes[0]["id"])[0]
            #    variables = self.get_variables(scope["variablesReference"])
            #    if len(variables) == 0:
            #        return_value = ""
            #    else:
            #        return_value = variables[0]["value"]
            #    break

            self.add_variable(frame_id, stackframes, stackrecording)
        i += 1
        if i > max_steps:
            self.restart_server()
            self.initialize()
            #TODO: reset any parameters needed
            return "Interrupted", stackrecording

        #	TODO: Find a way to know that we are at the end of the target function and go back to the main loop
        #if stackframes[0]["line"] in end_lines:
        #    self.evaluate("-exec fin", frame_id)
        #    self.wait("event", event="stopped")
        #else:
        #    self.step(thread_id=self.thread_id)
        #    self.wait("event", event="stopped")

        return return_value, stackrecording

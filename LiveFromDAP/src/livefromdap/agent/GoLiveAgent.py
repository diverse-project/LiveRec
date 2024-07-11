import os
import subprocess

from debugpy.common.messaging import JsonIOStream
from debugpy.common import sockets
from .BaseLiveAgent import BaseLiveAgent, DebuggeeTerminatedError
from tree_sitter import Language, Parser
from livefromdap.utils.StackRecording import Stackframe, StackRecording


class GoLiveAgent(BaseLiveAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = True
        self.compile_command = kwargs.get("compile_command", 'go build -gcflags="all=-N -l" -o {target_output} {'
                                                             'target_input}')
        self.runner_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner"))
        self.runner_name = "go_runner.go"
        self.runner_path_exec = os.path.abspath(os.path.join(self.runner_directory, "go_runner"))
        self.runner_path = os.path.abspath(os.path.join(self.runner_directory, self.runner_name))
        self.lang = Language(kwargs.get("tree_sitter_path", os.path.join(os.path.dirname(__file__), "..", "bin",
                                                                         "treesitter", "go.so")), 'go')
        self.parser = Parser()
        self.parser.set_language(self.lang)
        self.param_and_return_query_string = """
        (function_declaration
            name: (identifier) @func_name
            parameters: (parameter_list) @params
            result: (type_identifier) @return_type
        ) @funcdef
        """
        self.end_function_query_string = """
        (function_declaration
            name: (identifier) @fname
            (#match? @fname "{function_name}")
        ) @funcdef
        (return_statement) @return
        """
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
                error = self.server_process.stderr.readline()  # type: ignore
                # if address already in use
                if b"Error: listen EADDRINUSE: address already in use" in error:
                    # fidn the process that is using the port
                    p = subprocess.Popen(["lsof", "-i", ":9000"], stdout=subprocess.PIPE)
                    p.wait()
                    lsof_output = p.stdout.readlines()  # type: ignore
                    pid = lsof_output[-1].split()[1]
                    subprocess.Popen(["kill", pid])
                    self.start_server()
                    return
            output = self.server_process.stdout.readline()  # type: ignore
            # wait for : DAP server listening at: [::]:9000
            if b"DAP server listening at" in output:
                break

        self.main_server = sockets.create_client()
        self.main_server.connect(("localhost", 9000))
        self.main_io = JsonIOStream.from_socket(self.main_server)

    def stop_server(self):
        self.server_process.kill()

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
        self.server_process.close()

    def restart_server(self):
        self.server_process.kill()
        self.start_server()

    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [36])
        self.configuration_done()

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
                "supportsStartDebuggingRequest": True,
                "supportsConfigurationDoneRequest": True,
                "supportsSetExpression": True
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "noDebug": False,
                "name": "Launch",
                "program": self.runner_path,
                "rootPath": self.runner_directory,
                "cwd": self.runner_directory,
                "showGlobalVariables": True,
            }
        }
        self.io = self.main_io
        self.main_io.write_json(init_request)
        self.wait("response", command="initialize")
        self.main_io.write_json(launch_request)
        self.wait("response", command="launch")
        self.setup_runner_breakpoint()
        brk = self.wait("event", "stopped")
        self.thread_id = brk["body"]["threadId"]

    def compile(self, input_file=None, output_file=None):
        """Compile the target file"""
        compilation = subprocess.run(self.compile_command.format(target_input=input_file, target_output=output_file),
                                     shell=True, check=True)
        return compilation.returncode

    def get_param_and_return_type(self, node, source_code) -> (list[str], list[str]):
        params = node.child_by_field_name('parameters')
        result = node.child_by_field_name('result')

        # Extract parameters
        param_list = []
        if params:
            for param in params.children:
                if param.type == 'parameter_declaration':
                    param_type = param.child_by_field_name('type')
                    param_type_text = source_code[param_type.start_byte:param_type.end_byte].decode('utf-8')
                    param_list.append(param_type_text)

        # Extract return types
        return_list = []
        if result:
            if result.type == 'type_identifier':
                return_type_text = source_code[result.start_byte:result.end_byte].decode('utf-8')
                return_list.append(return_type_text)

        return param_list, return_list

    def process_file(self, path, function_name):
        with open(path, 'r') as file:
            code = file.read()
        function_node = None
        tree = self.parser.parse(bytes(code, "utf8"))
        query = self.lang.query(self.param_and_return_query_string.format(function_name=function_name))
        captures = query.captures(tree.root_node)
        for capture in captures:
            if capture[1] == 'func_name':
                func_name_text = code[capture[0].start_byte:capture[0].end_byte]
                if func_name_text == function_name:
                    function_node = capture[0].parent

        if function_node is None:
            raise Exception(f"Function {function_name} not found")
        else:
            return self.get_param_and_return_type(function_node, bytes(code, "utf8"))

    def get_end_line(self, path: str, function_name: str) -> list[int]:
        with open(path, 'r') as file:
            code = file.read()
        query = self.lang.query(self.end_function_query_string.format(function_name=function_name))
        captures = query.captures(self.parser.parse(bytes(code, "utf8")).root_node)
        captures = [c for c in captures if c[1] == "funcdef" or c[1] == "return"]
        if len(captures) == 0:
            raise Exception(f"Function {function_name} not found")
        else:
            res = []
            for capture in captures:
                if capture[1] == "funcdef":
                    res.append(capture[0].end_point[0] + 1)
                if capture[1] == "return":
                    res.append(capture[0].start_point[0] + 1)
            return res

    def add_variable(self, frame_id, stackframes, stackrecording):
        stackframe = stackframes[0]
        line = stackframe["line"]
        column = stackframe["column"]
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variablesReference"])
        height = len(stackframes) - self.initial_height
        recorded_stackframe = Stackframe(line, column, height, variables)
        stackrecording.add_stackframe(recorded_stackframe)

    def load_code(self, path: str):
        # if not path.endswith(".so"):
        #     # change the extension to .so
        #     compiled_path = path[:-3] + ".so"
        #     # compile the file
        #     self.compile(input_file=os.path.abspath(path), output_file=os.path.abspath(compiled_path))
        #     path = compiled_path
        frame_id = self.get_stackframes(thread_id=self.thread_id)[0]["id"]
        self.evaluate(f"call loadPlugin(\"{path}\")", frame_id)

    def execute(self, source_file: str, method: str, args: list[str], max_steps: int = 300) -> tuple[
        str, StackRecording]:
        breakpoint()
        frame_id = self.get_stackframes(thread_id=self.thread_id)[0]["id"]
        command = f"call callPluginFunction(\"{method}\", {args[0]})"
        self.evaluate(command, frame_id)

        self.set_function_breakpoint([method])
        end_lines: list[int] = self.get_end_line(source_file, method)

        self.next_breakpoint(thread_id=self.thread_id)
        self.wait("event", "stopped")

        stackrecording = StackRecording()
        self.initial_height = -1
        i = 0
        while True:
            stackframes = self.get_stackframes(thread_id=self.thread_id)
            if self.initial_height == -1:
                self.initial_height = len(stackframes)
            frame_id = stackframes[0]["id"]
            if stackframes[0]["name"] == "main()":
                return_value = None
                scope = self.get_scopes(stackframes[0]["id"])[0]
                variables = self.get_variables(scope["variablesReference"])
                if len(variables) == 0:
                    return_value = ""
                else:
                    return_value = variables[0]["value"]
                break

            self.add_variable(frame_id, stackframes, stackrecording)
            i += 1
            if i > max_steps:
                self.restart_server()
                self.initialize()
                self.current_loaded_shared_libraries = None
                return "Interrupted", stackrecording
            if stackframes[0]["line"] in end_lines:
                self.evaluate("-exec fin", frame_id)
                self.wait("event", event="stopped")
            else:
                self.step(thread_id=self.thread_id)
                self.wait("event", event="stopped")
        return return_value, stackrecording

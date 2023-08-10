import os
import subprocess
from tree_sitter import Language, Parser
from debugpy.common.messaging import JsonIOStream

from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .BaseLiveAgent import BaseLiveAgent

class CLiveAgent(BaseLiveAgent):
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.compile_command = kwargs.get("compile_command", "gcc -g -fPIC -shared -o {target_input} {target_output}")
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "c_runner.c"))
        self.runner_path_exec = kwargs.pop("runner_path_exec", os.path.join(os.path.dirname(__file__), "..", "runner", "c_runner"))
        self.dap_server_path = kwargs.get("dap_server_path", os.path.join(os.path.dirname(__file__), "..", "bin", "OpenDebugAD7", "OpenDebugAD7"))
        self.lang = Language(kwargs.get("tree_sitter_path", os.path.join(os.path.dirname(__file__), "..", "bin", "treesitter", "c.so")), 'c')
        self.parser = Parser()
        self.parser.set_language(self.lang)
        self.end_function_query_string = """
            (function_definition
                declarator: (function_declarator
                    declarator: (identifier) @fname
                    (#match? @fname "{function_name}")
                )
            ) @funcdef
            (return_statement) @return
        """
        self.current_loaded_shared_libraries = None
        self.main_thread_id = 0

    def start_server(self):
        """Create a subprocess with the agent"""
        self.server = subprocess.Popen(
            [self.dap_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.io = JsonIOStream.from_process(self.server)

    def stop_server(self) -> None:
        """Stop the Agent"""
        self.server.kill()
    
    def restart_server(self):
        self.server.kill()
        self.start_server()
         
    def initialize(self):
        """Send data to the agent"""
        init_request = init_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "initialize",
            "arguments": {
                "clientID": "vscode",
                "clientName": "Visual Studio Code",
                "adapterID": "cppdbg",
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
                "MIMode": "gdb",
                "miDebuggerPath": "/usr/bin/gdb",
                "setupCommands": [
                    {
                        "description": "Enable pretty-printing for gdb",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    }
                ],
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "name": "(gdb) Launch main",
                "type": "cppdbg",
                "request": "launch",
                "program": self.runner_path_exec,
                "args": [],
                "stopAtEntry": False,
                "cwd": os.getcwd(),
                "environment": [],
                "externalConsole": False,
                "MIMode": "gdb",
                "setupCommands": [
                    {
                        "description": "Enable pretty-printing for gdb",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    },
                    {
                        "description": "Set Disassembly Flavor to Intel",
                        "text": "-gdb-set disassembly-flavor intel",
                        "ignoreFailures": True
                    }
                ],
            }
        }
        self.io.write_json(init_request)
        self.io.write_json(launch_request)
        self.wait("event", "initialized")
        self.setup_runner_breakpoint()
        brk = self.wait("event", "stopped")
        self.main_thread_id = brk["body"]["threadId"]

    def compile(self, input_file=None, output_file=None):
        """Compile the target file"""
        compilation = subprocess.run(self.compile_command.format(target_input=input_file, target_output=output_file), shell=True, check=True)
        return compilation.returncode
    
    def get_end_line(self, path : str, function_name : str) -> list[int]:
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
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [14])
        self.configuration_done()

    def load_code(self, path: str):
        """Load the code to debug,
        compile it if needed"""
        # check if the file is not a shared library
        if not path.endswith(".so"):
            # change the extension to .so
            compiled_path = path[:-2] + ".so"
            # compile the file
            self.compile(input_file=os.path.abspath(path), output_file=os.path.abspath(compiled_path))
            path = compiled_path
        frame_id = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        libname = os.path.basename(path)
        if self.current_loaded_shared_libraries is not None:
            self.evaluate(f"-exec call close_lib()", frame_id)
        self.evaluate(f"-exec call load_lib(\"{path}\")", frame_id)
        self.current_loaded_shared_libraries = libname
            
    def add_variable(self, frame_id, stackframes, stackrecording):
        stackframe = stackframes[0]
        line = stackframe["line"]
        column = stackframe["column"]
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variablesReference"])
        height = len(stackframes) - self.initial_height
        recorded_stackframe = Stackframe(line, column, height, variables)
        stackrecording.add_stackframe(recorded_stackframe)
    
    def execute(self, source_file : str, method : str, args : list[str], max_steps : int=300) -> tuple[str, StackRecording]:
        self.set_function_breakpoint([method])
        command = f"-exec call {method}({','.join(args)})"
        frame_id = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        self.evaluate(command, frame_id)
        self.wait("event", event="stopped")
        end_lines : list[int] = self.get_end_line(source_file, method)
        stackrecording = StackRecording()
        return_value = ""
        self.initial_height = -1
        i = 0
        while True:
            stackframes = self.get_stackframes(thread_id=self.main_thread_id)
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
                self.step(thread_id=self.main_thread_id)
                self.wait("event", event="stopped")
        return return_value, stackrecording

import os
import subprocess
import time
from typing import Any, override
from tree_sitter import Language, Parser
from debugpy.common.messaging import JsonIOStream

from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .BaseDebugAgent import BaseDebugAgent


class CDebugAgent(BaseDebugAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compile_command = kwargs.get(
            "compile_command", "gcc -g -fPIC -shared {target_input} -o {target_output}")
        self.runner_path = kwargs.get("runner_path", os.path.join(
            os.path.dirname(__file__), "..", "runner", "c_runner.c"))
        self.runner_path_exec = kwargs.pop("runner_path_exec", os.path.join(
            os.path.dirname(__file__), "..", "runner", "c_runner"))
        self.dap_server_path = kwargs.get("dap_server_path", os.path.join(
            os.path.dirname(__file__), "..", "bin", "OpenDebugAD7", "OpenDebugAD7"))
        self.lang = Language(kwargs.get("tree_sitter_path", os.path.join(
            os.path.dirname(__file__), "..", "bin", "treesitter", "c.so")), 'c')
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
        self.buffered_breakpoints: dict[str, list[int]] = {}
        self.active_file = ""
        self.end_lines: list[list[int]] = []
        self.loaded_files: list[str] = []

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

    @override
    def set_breakpoint(self, path: str, lines: list[int]):
        if path == self.active_file:
            break_lines = lines + self.end_lines[-1]
            # print("\033[31m" + "lines:" + '\033[0m', break_lines)
            return super().set_breakpoint(path, break_lines)
        self.buffered_breakpoints[path] = lines

    def compile(self, input_file=None, output_file=None):
        """Compile the target file"""
        with open(input_file, "r+") as f:
            content = f.read()
            f.seek(0)
            f.write(
                '#include "/code/src/livefromdap/runner/polyglot_eval.c"\n' + content)
        compilation = subprocess.run(self.compile_command.format(
            target_input=input_file, target_output=output_file), shell=True, check=True)
        modif = subprocess.run(
            f"objcopy --redefine-sym main=polyglot_evaluation_main {output_file} {output_file}", shell=True, check=True)
        # print("command status:", compilation, modif)
        return compilation.returncode, modif.returncode

    def get_end_line(self, path: str, function_name: str) -> list[int]:
        with open(path, 'r') as file:
            code = file.read()
        query = self.lang.query(
            self.end_function_query_string.format(function_name=function_name))
        captures = query.captures(
            self.parser.parse(bytes(code, "utf8")).root_node)
        captures = [c for c in captures if c[1]
                    == "funcdef" or c[1] == "return"]
        if len(captures) == 0:
            raise Exception(f"Function {function_name} not found")
        else:
            res = []
            for capture in captures:
                # print("capture!", capture)
                if capture[1] == "funcdef":
                    # print("funcdef: ", capture[0].end_point[0] + 1)
                    res.append(capture[0].end_point[0] + 1)
                # if capture[1] == "return":
                #     res.append(capture[0].start_point[0] + 1)
                #     print("return: ", capture[0].start_point[0] + 1)
            return res

    def setup_runner_breakpoint(self):
        super().set_breakpoint(self.runner_path, [14])
        super().set_breakpoint(
            "/code/src/livefromdap/runner/polyglot_eval.c", [2])
        self.configuration_done()

    def load_code(self, path: str):
        """Load the code to debug,
        compile it if needed"""
        # print("loading: ", path)
        # check if the file is not a shared library
        if not path.endswith(".so"):
            # change the extension to .so
            compiled_path = path[:-2] + ".so"
            # compile the file
            # print(self.loaded_files)
            if path not in self.loaded_files:
                self.compile(input_file=os.path.abspath(path),
                         output_file=os.path.abspath(compiled_path))
                self.loaded_files.append(path)
            path = compiled_path
        frame_id = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        libname = os.path.basename(path)
        if self.current_loaded_shared_libraries == libname:
            return
        if self.current_loaded_shared_libraries is not None:
            self.evaluate(f"-exec call close_lib()", frame_id)
        self.evaluate(f"-exec call load_lib(\"{path}\")", frame_id)
        # print("libname", libname)
        self.current_loaded_shared_libraries = libname
        

    def finished_exec(self) -> bool:  # TODO
        stackframe = self.get_stackframes(thread_id=self.main_thread_id)[0]
        if stackframe["line"] in self.end_lines[-1]:
            # print("finished execution!", stackframe)
            # frameId = stackframe["id"]
            # scope = self.get_scopes(frameId)[0]
            # print("variables:", self.get_variables(scope["variablesReference"]))
            self.evaluate("-exec fin", stackframe["id"])
            self.end_lines.pop()
            self.wait("event", event="stopped")
            return True
        return False

    def get_return(self) -> Any:  # TODO:????
        stackframe = self.get_stackframes(thread_id=self.main_thread_id)[0]
        frameId = stackframe["id"]
        # scope = self.get_scopes(frameId)[0]
        # print("variables:", self.get_variables(scope["variablesReference"]))
        result = self.evaluate("$1", frameId)["body"]["result"]
        # print("result?", result)
        return result

    def in_polyglot_call(self) -> bool:
        stackframe = self.get_stackframes(thread_id=self.main_thread_id)[0]
        return stackframe["source"]["name"] == "polyglot_eval.c" and stackframe["line"] == 2
        

    def on_standby(self) -> bool:   # TODO
        stackframe = self.get_stackframes(thread_id=self.main_thread_id)[0]
        return stackframe["name"] == "main" and stackframe["line"] == 14

    def receive_return(self, return_value: Any) -> None:  
        frameId = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        self.evaluate(f"-exec set ret={return_value}", frameId)

    @override
    def get_exec_request(self) -> tuple[str, str]:
        frameId = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        lang = self.evaluate("lang", frameId)["body"]["result"].split()[1].strip("'").strip('"')
        frameId = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        code = self.evaluate("exec_code", frameId)["body"]["result"].split()[1].strip("'").strip('"')
        self.step(thread_id=self.main_thread_id)
        self.wait("event", "stopped")
        return lang, code

    def execute(self, filePath):
        # start = time.time()
        self.load_code(filePath)

        # need to flush buffered breakpoints for this file and combine with end lines
        self.end_lines.append(self.get_end_line(
            filePath, "main"))
        command = "-exec call polyglot_evaluation_main()"
        breakpoints = []
        try:
            for bp in self.buffered_breakpoints[filePath]:
                breakpoints.append(bp+1)  # adjust for the new include line
        except KeyError:
            pass
        self.active_file = filePath
        # print("\033[31m" + "end lines:" + '\033[0m', self.end_lines)
        # print("\033[31m" + "breakpoints:" + '\033[0m', breakpoints)
        self.set_breakpoint(filePath, breakpoints)
        self.buffered_breakpoints[filePath] = []  # clean the buffer
        frameId = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        res = self.evaluate(command, frameId)
        # end = time.time()
        # print("Time for C exec:", end - start)
        # print("execute res:", res)

    def start_execute(self, filePath):
        # start = time.time()
        self.load_code(filePath)

        # need to flush buffered breakpoints for this file and combine with end lines
        self.end_lines.append(self.get_end_line(
            filePath, "main"))
        # print("ending lines:", self.end_lines)
        # print("for path:", filePath)
        command = "-exec call polyglot_evaluation_main()"
        breakpoints = []
        try:
            for bp in self.buffered_breakpoints[filePath]:
                breakpoints.append(bp+1)  # adjust for the new include line
        except KeyError:
            pass
        self.active_file = filePath
        # print("\033[31m" + "end lines:" + '\033[0m', self.end_lines)
        # print("\033[31m" + "breakpoints:" + '\033[0m', breakpoints)
        self.set_function_breakpoint(["polyglot_evaluation_main"])
        self.set_breakpoint(filePath, breakpoints)
        self.buffered_breakpoints[filePath] = []  # clean the buffer
        frameId = self.get_stackframes(thread_id=self.main_thread_id)[0]["id"]
        # print("functions info:", self.evaluate("-exec info functions ^main", frameId))
        res = self.evaluate(command, frameId)
        # print("soft exec:", res)
        self.wait("event", "stopped")
        # end = time.time()
        # print("Time for C soft exec:", end - start)

import os
import subprocess
import sys
import time

from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseLiveAgent import BaseLiveAgent


class PolyglotLivExAgent(BaseLiveAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "py_runner.py"))
        self.polydebug_path = kwargs.get("polydebug_path", os.path.abspath(os.path.join("PolyDebug", "src", "main.py")))

    def start_server(self):
        """Create a subprocess with the agent"""
        # TODO: start polydebug and establish communication
        self.server = subprocess.Popen(
            ["python", self.polydebug_path],
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
                # "clientID": "vscode",
                # "clientName": "Visual Studio Code",
                # "adapterID": "python",
                # "pathFormat": "path",
                # "linesStartAt1": True,
                # "columnsStartAt1": True,
                # "supportsVariableType": True,
                # "supportsVariablePaging": True,
                # "supportsRunInTerminalRequest": True,
                # "locale": "en",
                # "supportsProgressReporting": True,
                # "supportsInvalidatedEvent": True,
                # "supportsMemoryReferences": True,
                # "supportsArgsCanBeInterpretedByShell": True,
                # "supportsMemoryEvent": True,
                # "supportsStartDebuggingRequest": True
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
        self.next_breakpoint()
        self.wait("event", "stopped")
        return 5
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [12,49])
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
        probes_by_loc = {}
        scoped_probes = {}
        recorded_probes = {}
        for probe in probes:
            probes_by_loc[int(probe["line"])] = probe # TODO: support multiple files
            # We need to check the probes ahead of time to see if there are cross-language scopes involved, and ready breakpoints for these
            probe_scopes = probe["expr"]["scopes"]
            if probe_scopes != []:
                # print(f"[DBG] Scopes: {probe_scopes}")
                self.set_function_breakpoint([probe_scopes[-1]])
                scoped_probes[probe_scopes[-1]] = probe

        while True:
            start = time.time()
            stacktrace = self.get_stackframes()
            # print(f"[DBG] Breakpointed at {stacktrace[0]}")
            if initial_height is None:
                initial_height = len(stacktrace)
                height = 0
            else:
                height = len(stacktrace) - initial_height
            if stacktrace[0]["name"] == "<module>" and stacktrace[0]["line"] == 49:
                break
            # We need to get local variables
            scope = self.get_scopes(stacktrace[0]["id"])[0]
            variables = self.get_variables(scope["variablesReference"])
            probed_variables = variables
            probe_var = None
            probed_expr = None
            line_number = stacktrace[0]["line"]
            if (funcName := stacktrace[0]["name"].removeprefix("global.")) in scoped_probes:
                future_probe = scoped_probes[funcName]
                step_count = 0
                # print(f"[DBG] Probe: {scoped_probes[funcName]}")
                # TODO: check call stack matches scopes
                # TODO: step until specific point in the function
                # We now need to record the value of the target expression for the future probe while stepping out
                step_start = time.time()
                while (frame := self.get_stackframes()[0])["name"].removeprefix("global.") == funcName:
                    try:
                        tmp_value = self.evaluate(future_probe["expr"]["target"], frame["id"])["body"]["body"]["result"]
                    except KeyError:
                        pass
                    self.step()
                    end = time.time()
                    print(f"Foreign recording time: {end-step_start}")
                    step_start = time.time()
                # print(f"[DBG] Exited {self.get_stackframes()[0]}")
                recorded_probes[
                    (int(future_probe["line"]), 
                    future_probe["expr"]["lang"], 
                    funcName)
                    ] = tmp_value
                
                self.next_breakpoint()
                continue
            for var in variables:
                match var["name"]:
                    case "line":
                        line_number = int(var["value"])
                    case "expr":
                        probed_expr = var["value"].strip("'")
                    case "ret":
                        probe_var = var
            # print(f"[DBG] Line: {line_number}")
            try:
                current_probe = probes_by_loc[line_number]
                # print(f"[DBG] Selected probe {current_probe}")
                if current_probe["expr"]["lang"] != "":
                    stackframe = self._resolve_polyglot_probe(current_probe, stacktrace, recorded_probes)
                    stackrecording.add_stackframe(stackframe)
                    end = time.time()
                    print(f"Probe time: {end-start}")
                    self.next_breakpoint()
                    continue
            except KeyError as e:
                # print(f"[DBG] Key error: {e}")
                pass
            if stacktrace[0]["name"] == "probe" and line_number not in probes_by_loc:
                self.next_breakpoint()
                continue
            elif probe_var is not None and line_number in probes_by_loc:
                probe_var["name"] = probed_expr
                probe_var["evaluateName"] = probed_expr
                probed_variables = [probe_var]
            stackframe = Stackframe(line_number-1, stacktrace[0]["column"], 0, probed_variables)
            stackrecording.add_stackframe(stackframe)
            end = time.time()
            print(f"Probe time: {end-start}")
            i += 1
            if i > max_steps:
                # we need to pop the current frame
                self.restart_server()
                self.initialize()
                return "Interrupted", stackrecording
            self.next_breakpoint()
        # We are now out of the function, we need to get the return value
        scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])
        return_value = None
        for variable in variables:
            if variable["name"] == f'res':
                return_value = variable["value"]
        for i in range(2): # Needed to reset the debugger agent loop
            self.next_breakpoint()
            self.wait("event", "stopped")
        return return_value, stackrecording
    
    def _resolve_polyglot_probe(self, current_probe, stacktrace, recorded_probes):
        # print(f"[DBG] Resolving probe: {current_probe}")
        # print(f"[DBG] Recorded probes: {recorded_probes}")
        if (key := 
            (int(current_probe["line"]), 
             current_probe["expr"]["lang"], 
             current_probe["expr"]["scopes"][-1])
             ) in recorded_probes:
            probed_var = {}
            probed_var["name"] = current_probe["expr"]["target"]
            probed_var["evaluateName"] = current_probe["expr"]["target"]
            probed_var["value"] = recorded_probes[key]
            # print(f"[DBG] Recorded probe var: {probed_var}")
        elif current_probe["expr"]["lang"] == "JS":
            previous_lang = self.switch_dap_lang("js")
            js_frame = self.get_stackframes()
            js_frameid = js_frame[0]["id"]
            probe_value = self.evaluate(current_probe["expr"]["target"], js_frameid)["body"]["body"]
            # print(f"[DBG] Value: {probe_value}")
            probed_var = {}
            probed_var["name"] = current_probe["expr"]["target"]
            probed_var["evaluateName"] = current_probe["expr"]["target"]
            try:
                probed_var["value"] = probe_value["result"]
            except KeyError:
                print(f"[DBG] Eval result could not be retrieved from: {probe_value}")
            # TODO: either pre-process polyglot probes or have polydebug record variables
            self.switch_dap_lang(previous_lang)
        elif current_probe["expr"]["lang"]  == "PY":
            raise NotImplementedError() #TODO
        else:
            raise NotImplementedError()
        return Stackframe(current_probe["line"]-1, stacktrace[0]["column"], 0, [probed_var])
    

    def switch_dap_lang(self, lang : str) -> str:
        """Changes the active DAP server of PolyDebug to the specified language
        WARNING: make sure to set the language back once you are done doing operations in the new language.

        Args:
            lang (str): the language id to set to

        Returns:
            str: the previous language id
        """
        switch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "switchLanguage",
            "arguments": {
                "language": lang
            }
        }
        self.io.write_json(switch_request)
        output = self.wait("response", command="switchLanguage")
        return output["body"]["previous"]
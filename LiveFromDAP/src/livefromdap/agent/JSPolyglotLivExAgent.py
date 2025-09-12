import os
import subprocess
import sys
import time

from livefromdap.agent.JavascriptLiveAgent import JavaScriptPreprocessor
import instrumentation as instr
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseLiveAgent import BaseLiveAgent


class JSPolyglotLivExAgent(BaseLiveAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner_path = kwargs.get("runner_path", os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "runner", "livex_runner.js")))
        self.polydebug_path = kwargs.get("polydebug_path", os.path.abspath(
            os.path.join("PolyDebug", "src", "main.py")))

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
        self.stop_server()
        self.start_server()

    def stop_request(self):
        stop_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "stop",
            "arguments": {

            }
        }
        self.io.write_json(stop_request)
        self.wait("response", command="stop")

    def stop_server(self):
        """Kill the subprocess"""
        self.stop_request()
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
                
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "program": self.runner_path,
            }
        }
        self.io.write_json(init_request)
        # self.io.write_json(launch_request)
        self.wait("event", "initialized")
        self.switch_dap_lang("js")
        self.setup_runner_breakpoint()
        self.next_breakpoint()
        self.wait("event", "stopped")
        return 5

    def setup_runner_breakpoint(self):
        self.configuration_done()

    def load_code(self, path: str):
        """For this agent, loading code is loading a class in the runner"""
        jspp = JavaScriptPreprocessor(path, path)
        # self._entry_line[path] = jspp.functions
        stacktrace = self.get_stackframes()
        frame_id = stacktrace[0]["id"]
        self.evaluate(f'livexLoadFile("{path}")', frame_id)

    def execute(self, method, args, probes, max_steps=50):
        self.start_method_exec(method, args)
        stackrecording = StackRecording()
        next_method = self.next_breakpoint
        probes_by_loc, scoped_probes = self.setup_probe_breakpoints(probes)
        recorded_probes = {}
        # We are now in the function, we need to get all information, step, and check if we are still in the function
        self.record_args(stackrecording)
        next_method()
        stacktrace = self.get_stackframes()
        while not (stacktrace[0]["name"] == "<anonymous>" and stacktrace[0]["line"] == 60):
            # print(f"[DBG] Stopped at {stacktrace[0]}")
            next_method = self.handle_stop(
                stacktrace, method, recorded_probes, scoped_probes, probes_by_loc, stackrecording) or next_method
            next_method()
            stacktrace = self.get_stackframes()
        return self.get_function_return(stacktrace, stackrecording)

    def start_method_exec(self, method, args):
        self.set_function_breakpoint([method])
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        res1 = self.evaluate(f"target_function = {method}", frameId)
        res2 = self.evaluate(f"target_args = [{','.join(args)}]", frameId)
        # We need to run the debug agent loop until we are on a breakpoint in the target method
        while True:
            stacktrace = self.get_stackframes()
            if stacktrace[0]["name"].removeprefix("global.") == method:
                break
            self.next_breakpoint()
            self.wait("event", "stopped")

    def setup_probe_breakpoints(self, probes):
        probes_by_loc = {}
        scoped_probes = {}
        for probe in probes:
            # TODO: support multiple files
            probes_by_loc[int(probe["line"])] = probe
            # We need to check the probes ahead of time to see if there are cross-language scopes involved, and ready breakpoints for these
            probe_scopes = probe["expr"]["scopes"]
            if probe_scopes != []:
                # print(f"[DBG] Scopes: {probe_scopes}")
                scoped_probes.update(  # Setup function-to-probes mapping
                    {(probe["expr"]["lang"].lower(), probe_scopes[-1]):
                     scoped_probes.get(
                         (probe["expr"]["lang"].lower(), probe_scopes[-1]), []) + [probe]
                     })
        self.set_function_breakpoint([key[1] for key in scoped_probes.keys()])
        return probes_by_loc, scoped_probes

    def record_args(self, stackrecording: StackRecording):
        stacktrace = self.get_stackframes()
        scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])
        stackframe = Stackframe(
            stacktrace[0]["line"]-1, stacktrace[0]["column"], 0, variables)
        stackrecording.add_stackframe(stackframe)

    def handle_stop(self, stacktrace, method, recorded_probes, scoped_probes, probes_by_loc, stackrecording: StackRecording):
        func_name = stacktrace[0]["name"].removeprefix("global.")
        if (self.get_dap_lang(), func_name) in scoped_probes:
            self.resolve_foreign_recording(
                stacktrace, recorded_probes, scoped_probes)
            next_method = self.step
        elif func_name == "probe":
            self.resolve_probe(stacktrace, recorded_probes,
                               probes_by_loc, stackrecording)
            next_method = None  # dont change the way to resume execution when meeting a probe
        elif func_name == method:
            next_method = self.next_breakpoint
        else:
            # We are neither in a probe, a function that needs recording, the original method, or at the end of the execution.
            # We need to step out until we are back at one of those points.
            next_method = self.step_out
        return next_method

    def resolve_foreign_recording(self, stacktrace, recorded_probes, scoped_probes):
        start = time.time()
        func_name = stacktrace[0]["name"].removeprefix("global.")
        probes_to_record = scoped_probes[self.get_dap_lang(), func_name]
        for current_probe in probes_to_record:
            key = (int(current_probe["line"]),
                   current_probe["expr"]["lang"],
                   current_probe["expr"]["scopes"][-1])
            try:
                value = self.evaluate(current_probe["expr"]["target"], stacktrace[0]["id"])[
                    "body"]["body"]["result"]
                recorded_probes[key] = value
            except KeyError:
                pass
        end = time.time()
        instr.py_foreign_record_times.append(end-start)

    def resolve_probe(self, stacktrace, recorded_probes, probes_by_loc, stackrecording: StackRecording):
        start = time.time()
        scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])
        for var in variables:
            match var["name"]:
                case "line":
                    line_number = int(var["value"])
                case "expr":
                    probed_expr = var["value"].strip("'")
                case "ret":  # TODO: remove?
                    probed_var = var

        if stacktrace[0]["name"] == "probe" and line_number not in probes_by_loc:
            print(f"Reached unselected probe at line {line_number}")
            return
        current_probe = probes_by_loc[line_number]
        if len(current_probe["expr"]["scopes"]) == 0:
            # no scopes = simple probe, just evaluate expr

            if current_probe["expr"]["lang"] != "":
                previous_lang = self.switch_dap_lang(
                    current_probe["expr"]["lang"].lower())
                foreign_frame_id = self.get_stackframes()[0]["id"]
                probed_value = self.evaluate(probed_expr, foreign_frame_id)
                probed_var = {}
            else:
                self.step_out()
                new_frame = self.get_stackframes()[0]
                probed_value = self.evaluate(current_probe["expr"]["target"], new_frame["id"])
            probed_var["name"] = probed_expr
            probed_var["evaluateName"] = probed_expr
            try:
                probed_var["value"] = probed_value["body"]["body"]["result"]
            except KeyError:
                print(
                    f"[DBG] Eval result could not be retrieved from: {probed_value}")
                probed_var["value"] = "[Error] Could not retrieve value"
            if current_probe["expr"]["lang"] != "":
                self.switch_dap_lang(previous_lang)

        else:
            # scopes present = complex probe, fetch previously recorded probed value
            if (key :=  # TODO: implement a probe ID
                    (int(current_probe["line"]),
                     current_probe["expr"]["lang"],
                     current_probe["expr"]["scopes"][-1])
                    ) in recorded_probes:
                probed_var = {}
                probed_var["name"] = current_probe["expr"]["target"]
                probed_var["evaluateName"] = current_probe["expr"]["target"]
                probed_var["value"] = recorded_probes[key]
            else:
                print(f"[DBG] Dumping probe map: {recorded_probes}")
                raise Exception(
                    f"Error: could not find recorded value for probe {current_probe}")

        frame = Stackframe(
            current_probe["line"]-1, stacktrace[0]["column"], 0, [probed_var])
        stackrecording.add_stackframe(frame)
        end = time.time()
        instr.js_local_probe_times.append(end-start)

    def get_function_return(self, stacktrace, stackrecording: StackRecording):
        # We are now out of the function, we need to get the return value
        scope = self.get_scopes(stacktrace[0]["id"])[0]
        variables = self.get_variables(scope["variablesReference"])
        return_value = None
        for variable in variables:
            if variable["name"] == f'result':
                return_value = variable["value"]
        for i in range(2):  # Needed to reset the debugger agent loop
            self.next_breakpoint()
            self.wait("event", "stopped")
        return return_value, stackrecording



    def switch_dap_lang(self, lang: str) -> str:
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

    def get_dap_lang(self) -> str:
        """Checks the language for the active DAP server of PolyDebug

        Returns:
            str: the current language id
        """
        getlang_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "getLanguage",
            "arguments": {
            }
        }
        self.io.write_json(getlang_request)
        output = self.wait("response", command="getLanguage")
        return output["body"]["current"]

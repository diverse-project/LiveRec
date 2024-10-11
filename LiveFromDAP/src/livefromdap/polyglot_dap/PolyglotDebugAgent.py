import os
import subprocess
import sys
import time
import re
from typing import Any, override

from livefromdap.polyglot_dap.JavascriptDebugAgent import JavascriptDebugAgent
from livefromdap.polyglot_dap.PythonDebugAgent import PythonDebugAgent
from livefromdap.polyglot_dap.CDebugAgent import CDebugAgent
import debugpy
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseDebugAgent import BaseDebugAgent


class PolyglotDebugAgent(BaseDebugAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debuggers: dict[str, BaseDebugAgent] = {
            "py": PythonDebugAgent(), "js": JavascriptDebugAgent(), "c": CDebugAgent()}
        self.active_dap: BaseDebugAgent = self.debuggers["py"]
        self.call_stack: list[BaseDebugAgent] = []
        # self.debug = True
        # self.time_since = time.time()
        

    def set_debug_mode(self, dbg: bool, target:str = ""):
        if target == "":
            self.debug = dbg
            for agent in self.debuggers.values():
                agent.debug = self.debug
        else:
            self.debuggers[target].debug = dbg

    def start_server(self):
        """Create a subprocess with the agent"""
        for agent in self.debuggers.values():
            agent.start_server()

    def restart_server(self):
        for agent in self.debuggers.values():
            agent.restart_server()

    def stop_server(self):
        """Kill the subprocess"""
        for agent in self.debuggers.values():
            agent.stop_server()

    def initialize(self):
        """Send data to the agent"""
        for agent in self.debuggers.values():
            agent.initialize()

    def setup_runner_breakpoint(self):
        for agent in self.debuggers.values():
            agent.setup_runner_breakpoint()

    def load_code(self, path: str):
        lang_ext = path.split(".").pop()
        self.active_dap = self.debuggers[lang_ext]
        if lang_ext == "c":
            self.active_dap.start_execute(path)
        else:
            self.active_dap.load_code(path)

    @override
    def set_breakpoint(self, path: str, lines: list):
        for agent in self.debuggers.values():
            agent.set_breakpoint(path, lines)

    @override
    def new_seq(self):
        return self.active_dap.new_seq()

    @override
    def _handleRunInTerminal(self, output: dict):
        return self.active_dap._handleRunInTerminal(output)

    @override
    def get_stackframes(self, thread_id: int = 1, levels: int = 100) -> list:
        print("stackframe")
        return self.active_dap.get_stackframes(self._handle_thread_id(thread_id), levels)

    def _handle_thread_id(self, thread_id: int = 1) -> int:
        try:
            return self.active_dap.main_thread_id
        except AttributeError:
            return thread_id

    @override
    def get_scopes(self, frame_id: int) -> list:
        print("scopes")
        return self.active_dap.get_scopes(frame_id)

    @override
    def get_variables(self, scope_id: int) -> list:
        print("variables")
        return self.active_dap.get_variables(scope_id)

    @override
    def evaluate(self, expression: str, frame_id: int, context: str = "repl") -> dict:
        return self.active_dap.evaluate(expression, frame_id, context)

    @override
    def wait(self, type: str, event: str = "", command: str = "") -> dict:
        self.active_dap.debug = self.debug
        return self.active_dap.wait(type, event, command)

    def _handle_polyglot(self):
        while True:
            # print("handling stack:", self.get_stackframes()[0])
            # start = time.time()
            if self.active_dap.in_polyglot_call():
                # end = time.time()
                # print("Time to check if polyglot call:", end - start)
                # start = time.time()
                lang, filePath = self.active_dap.get_exec_request()
                # print("\033[31m" + "{0}".format("polyglot call at") + '\033[0m', lang, filePath)
                # self.time_since = time.time() - self.time_since
                # print("time?", self.time_since)

                self.call_stack.append(self.active_dap)
                self.active_dap = self.debuggers[lang]
                # print(self.active_dap)
                # end = time.time()
                # print("Polyglot call time:", end - start)
                self.active_dap.execute(filePath)
                # self.next_breakpoint()
            elif self.active_dap.finished_exec():
                # end = time.time()
                # print("Time to check if execution finished:", end - start)
                # start = time.time()
                return_value = self.active_dap.get_return()
                self.active_dap.next_breakpoint(self._handle_thread_id())
                old_dap = self.active_dap
                try:
                    self.active_dap = self.call_stack.pop()
                    return_value = self._convert_data(old_dap, self.active_dap, return_value)
                except IndexError:
                    break
                self.active_dap.receive_return(return_value)
                # end = time.time()
                # print("Polyglot return receive time:", end - start)
                self.active_dap.next_breakpoint(self._handle_thread_id())
            else:
                break

    def _convert_data(self, origin, target, data):
        if isinstance(origin, JavascriptDebugAgent) and isinstance(target, PythonDebugAgent):
            array_parse = re.fullmatch(r"\([0-9]*\) (\[([0-9]+, )*[0-9]+\])", data)
            if array_parse is not None:
                arr = array_parse.group(1)
                # print("Successfully converted JS array to Python array: ", arr)
                return arr
        return data



    @override
    def next_breakpoint(self, thread_id: int = 1):
        # print("\033[31m" + "Continuing" + '\033[0m')
        self.active_dap.next_breakpoint(self._handle_thread_id(thread_id))
        self._handle_polyglot()
        return "stopped breakpoint"
        

    @override
    def step(self, thread_id: int = 1):
        self.active_dap.step(self._handle_thread_id(thread_id))
        self._handle_polyglot()
        return "stopped step"
    
    @override
    def step_in(self, thread_id: int = 1):
        self.active_dap.step_in(self._handle_thread_id(thread_id))
        self._handle_polyglot()
        return "stopped step"

    @override
    def step_out(self, thread_id: int = 1):
        self.active_dap.step_out(self._handle_thread_id(thread_id))
        self._handle_polyglot()
        return "stopped step"

    def execute(self, filePath):
        pass

    def finished_exec(self) -> bool:
        return super().finished_exec()

    def get_exec_request(self) -> tuple[str, str]:
        return super().get_exec_request()

    def get_return(self) -> Any:
        return super().get_return()

    def in_polyglot_call(self) -> bool:
        return super().in_polyglot_call()

    def on_standby(self) -> bool:
        return super().on_standby()

    def receive_return(self, return_value: Any) -> None:
        return super().receive_return(return_value)

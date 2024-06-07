import os
import subprocess
import sys
import time
from typing import Any, override

from livefromdap.polyglot_dap.JavascriptDebugAgent import JavascriptDebugAgent
from livefromdap.polyglot_dap.PythonDebugAgent import PythonDebugAgent
import debugpy
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseDebugAgent import BaseDebugAgent


class PolyglotDebugAgent(BaseDebugAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debuggers: dict[str, BaseDebugAgent] = {
            "py": PythonDebugAgent(), "js": JavascriptDebugAgent()}
        self.active_dap: BaseDebugAgent = self.debuggers["py"]
        self.call_stack: list[BaseDebugAgent] = []
        # self.debug = True
        for agent in self.debuggers.values():
            agent.debug = self.debug

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
        return self.active_dap.get_stackframes(thread_id, levels)

    @override
    def get_scopes(self, frame_id: int) -> list:
        return self.active_dap.get_scopes(frame_id)

    @override
    def get_variables(self, scope_id: int) -> list:
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
            if self.active_dap.in_polyglot_call():
                lang, filePath = self.active_dap.get_exec_request()
                print("polyglot call at", lang, filePath)
                self.call_stack.append(self.active_dap)
                self.active_dap = self.debuggers[lang]
                self.active_dap.execute(filePath)
                self.next_breakpoint()
            elif self.active_dap.finished_exec():
                return_value = self.active_dap.get_return()
                self.active_dap = self.call_stack.pop()
                self.active_dap.receive_return(return_value)
                self.next_breakpoint()
            else:
                break


    @override
    def next_breakpoint(self, thread_id: int = 1):
        self.active_dap.next_breakpoint(thread_id)
        self._handle_polyglot()

    @override
    def step(self, thread_id: int = 1):
        self.active_dap.step(thread_id)
        self._handle_polyglot()

    @override
    def step_out(self, thread_id: int = 1):
        self.active_dap.step_out(thread_id)
        self._handle_polyglot()

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

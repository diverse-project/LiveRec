import os
import subprocess
import sys
import time
from typing import override

from LiveFromDAP.src.livefromdap.polyglot_dap.JavascriptDebugAgent import JavascriptDebugAgent
from LiveFromDAP.src.livefromdap.polyglot_dap.PythonDebugAgent import PythonDebugAgent
import debugpy
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseDebugAgent import BaseDebugAgent


class PolyglotDebugAgent(BaseDebugAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debuggers: dict[str, BaseDebugAgent] = {"py": PythonDebugAgent(), "js": JavascriptDebugAgent()}
        self.active_dap: BaseDebugAgent = self.debuggers["py"]
        self.call_stack: list[BaseDebugAgent] = []
        # self.debug = True

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
        pass

    def handle_polyglot(self):
        if self.active_dap.in_polyglot_call():
            lang, filePath = self.active_dap.get_exec_request()
            self.call_stack.append(self.active_dap)
            self.active_dap = self.debuggers[lang]
            self.active_dap.execute(filePath)
        elif self.active_dap.finished_exec():
            return_value = self.active_dap.get_return()
            self.active_dap = self.call_stack.pop()
            self.active_dap.receive_return(return_value)

    @override
    def next_breakpoint(self, thread_id: int = 1):
        self.active_dap.next_breakpoint(thread_id)
        self.handle_polyglot()

    @override
    def step(self, thread_id: int = 1):
        self.active_dap.step(thread_id)
        self.handle_polyglot()
    
    @override
    def step_out(self, thread_id: int = 1):
        self.active_dap.step_out(thread_id)
        self.handle_polyglot()
    

    def execute(self, filePath):
        pass
    
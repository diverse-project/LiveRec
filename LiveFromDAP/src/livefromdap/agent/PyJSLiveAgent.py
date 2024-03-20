import os
import subprocess
import sys

import debugpy
from debugpy.common.messaging import JsonIOStream
from livefromdap.utils.StackRecording import Stackframe, StackRecording

from .BaseLiveAgent import BaseLiveAgent
from .PythonLiveAgent import PythonLiveAgent
from .JavascriptLiveAgent import JavascriptLiveAgent
import re
import ast as python_ast


class PyJSLiveAgent(BaseLiveAgent):
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.py_agent = PythonLiveAgent(*args, **kwargs)
        self.js_agent = JavascriptLiveAgent(*args, **kwargs)


    def start_server(self):
        """Create a subprocess with the agent"""

        self.py_agent.start_server()
        self.js_agent.start_server()
    
    def restart_server(self):
        self.py_agent.restart_server()
        self.js_agent.restart_server()

    def stop_server(self):
        """Kill the subprocess"""
        self.py_agent.stop_server()
        self.js_agent.stop_server()
    
    def initialize(self):
        """Send data to the agent"""
        self.py_agent.initialize()
        self.js_agent.initialize()
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [16])
        self.configuration_done()
    
    def load_code(self, path: str):
        stacktrace = self.py_agent.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.py_agent.evaluate(f"set_import('{os.path.abspath(path)}')", frameId)
        self.py_agent.next_breakpoint()
        self.py_agent.wait("event", "stopped")
        with open(os.path.abspath(path)) as f:
            self.source_code = f.readlines()
            
    def execute(self, method, args, max_steps=50):
        self.py_agent.set_function_breakpoint([method])
        stacktrace = self.py_agent.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.py_agent.evaluate(f"set_method('{method}',[{','.join(args)}])", frameId)
        # We need to run the debug agent loop until we are on a breakpoint in the target method
        stackrecording = StackRecording()
        while True:
            stacktrace = self.py_agent.get_stackframes()
            if stacktrace[0]["name"] == method:
                break
            self.py_agent.next_breakpoint()
            self.py_agent.wait("event", "stopped")
        # We are now in the function, we need to get all information, step, and check if we are still in the function
        scope = None
        initial_height = None
        polyglot_var = None
        polyglot_result = None
        i = 0
        while True:
            stacktrace = self.py_agent.get_stackframes()
            if initial_height is None:
                initial_height = len(stacktrace)
                height = 0
            else:
                height = len(stacktrace) - initial_height
            if stacktrace[0]["name"] != method:
                break
            # We need to get local variables
            if not scope:
                scope = self.py_agent.get_scopes(stacktrace[0]["id"])[0]
            variables = self.py_agent.get_variables(scope["variablesReference"])
            stackframe = Stackframe(stacktrace[0]["line"], stacktrace[0]["column"], height, variables)
            stackrecording.add_stackframe(stackframe)
            i += 1
            if i > max_steps:
                # we need to pop the current frame
                self.restart_server()
                self.initialize()
                return "Interrupted", stackrecording
            self.py_agent.step()
            # handle the polyglot (JS) case
            if polyglot_var is not None and polyglot_result is not None:
                try:
                    self.py_agent.set_expression(polyglot_var, polyglot_result, stacktrace[0]["id"])
                except:
                    pass
                polyglot_var = None
                polyglot_result = None
            if (l := stacktrace[0]["line"]) != 0 and (m := re.match(r".*?polyglotEval\((.*?),(.*?)\)", (stmt := self.source_code[l]))):
                polyglot_node = python_ast.parse(stmt.strip())
                visitor = IsAssignOrExpr()
                visitor.generic_visit(polyglot_node)
                if visitor.result is not None:
                    polyglot_var = visitor.result
                    polyglot_result = (self.js_agent.evaluate(
                        m.group(2).strip().strip('"'), 
                        self.js_agent.get_stackframes()[0]["id"])
                                .get("body")
                                .get("result")
                                .strip("'")
                    )
        # We are now out of the function, we need to get the return value
        self.py_agent.step()
        scope = self.py_agent.get_scopes(stacktrace[0]["id"])[0]
        variables = self.py_agent.get_variables(scope["variablesReference"])
        return_value = None
        for variable in variables:
            if variable["name"] == f'(return) {method}':
                return_value = variable["value"]
        for i in range(2): # Needed to reset the debugger agent loop
            self.py_agent.next_breakpoint()
            self.py_agent.wait("event", "stopped")
        return return_value, stackrecording
    
class IsAssignOrExpr(python_ast.NodeVisitor):

    def __init__(self):
        self.result = None

    def visit_Assign(self, node: python_ast.Assign):
        self.result = node.targets[0].id
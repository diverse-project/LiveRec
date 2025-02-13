import os
import subprocess
import sys
from time import sleep


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
            if (call_name := self.py_agent.get_stackframes()[0]["name"]) != method and call_name == "polyglotEval":
                    # move to right before function returns
                    self.py_agent.step()
                    # we now need to have the JS agent evaluate the expression
                    py_stackframes = self.py_agent.get_stackframes()
                    js_stackframes = self.js_agent.get_stackframes()
                    code = self.py_agent.evaluate("j", py_stackframes[0]["id"]).get("body").get("result").strip("'")
                    polyglot_result = self.js_agent.evaluate(code, js_stackframes[0]["id"]).get("body").get("result")
                    # set return value with the polyglot evaluation result, then exit polyglot call and resume normal execution
                    self.py_agent.set_expression("ret", polyglot_result, py_stackframes[0]["id"])
                    self.py_agent.step_out()
                    # additional step to account for the live loop logic (i.e. not process the line twice)
                    self.py_agent.step()
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
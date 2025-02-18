from typing import Any
from livefromdap.utils.StackRecording import StackRecording
from webdemo.AutoAgent import AutoLiveAgent
from livefromdap.agent.PythonLiveAgent2 import PythonLiveAgent
import json
import ast as python_ast

class AutoPythonLiveAgent(AutoLiveAgent):
    def __init__(self, raw=False):
        self.raw = raw
        self.agent = PythonLiveAgent(debug=False)
        self.agent.start_server()
        self.agent.initialize()
        self.previous_ast = None
        self.source_path = None
    
    def restart(self):
        self.agent.stop_server()
        self.agent.start_server()
        self.agent.initialize()

    def get_code(self):
        if self.source_path is None:
            return None
        with open(self.source_path, "r") as f:
            return f.read()

    def check_if_parsable(self):
        code = self.get_code()
        if code is None:
            return False, False
        parsable = False
        changed = False
        try:
            ast = python_ast.parse(code)
            parsable = True
        except Exception as e:
            print("Error parsing code", e)
            return False, False
        
        if self.previous_ast is None:
            self.previous_ast = ast
            changed = True
        elif python_ast.dump(ast) != python_ast.dump(self.previous_ast):
            self.previous_ast = ast
            changed = True
        return parsable, changed
    
    def update_code(self):
        is_parsable, changed = self.check_if_parsable()
        if is_parsable and changed and self.source_path is not None:
            self.agent.load_code()
            return True
        return False
    
    def set_source_path(self, path):
        self.source_path = path
        self.agent.set_source_path(path)
        

    def construct_result_json(self, method, output: tuple[Any, StackRecording]):
        return_value, stacktrace = output
        print("stacktrace", stacktrace, stacktrace.last_stackframe)
        stacktrace.last_stackframe.variables.append({"name":"return", "value":return_value})
        return json.dumps({
            "return_value": return_value,
            "stacktrace": stacktrace.to_json()
        })
    
    def execute(self, method : str, args : dict):
        output = self.agent.execute(method, args)
        return self.construct_result_json(method, output)
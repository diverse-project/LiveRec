import os
import ast as python_ast
from livefromdap.agent.AdvancedPythonLiveAgent import AdvancedPythonLiveAgent
from prettyprinter.PythonPrettyPrinter import PythonPrettyPrinter
from .base import BaseAutoLiveAgent

class AutoAdvancedPythonLiveAgent(BaseAutoLiveAgent):
    def __init__(self):
        super().__init__(raw=True)
        self.agent = AdvancedPythonLiveAgent(debug=False)
        self.agent.start_server()
        self.agent.initialize()
        self.source_path = ""
        self.previous_ast = None


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
            return False, False

        if self.previous_ast is None:
            self.previous_ast = ast
            changed = True
        elif python_ast.dump(ast) != python_ast.dump(self.previous_ast):
            self.previous_ast = ast
            changed = True
        return parsable, changed

    def update_code(self, code):
        is_parsable, changed = self.check_if_parsable()
        if is_parsable and changed and self.source_path is not None:
            self.agent.load_code()
            return True
        return False
    
    def set_source_path(self, path):
        self.source_path = path
        self.agent.set_source_path(path)
        
    
    def execute(self, method : str, args : dict):
        output = self.agent.execute(method, args)
        return self.construct_result_json(method, output, PythonPrettyPrinter)

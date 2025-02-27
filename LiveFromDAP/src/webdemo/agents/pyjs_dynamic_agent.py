import os
import ast as python_ast
from livefromdap.agent.PyJSLiveAgent import PyJSLiveAgent
from prettyprinter.PythonPrettyPrinter import PythonPrettyPrinter
from .base import BaseAutoLiveAgent

class AutoPyJSDynamicAgent(BaseAutoLiveAgent):
    def __init__(self, raw=False):
        super().__init__(raw)
        self.agent = PyJSLiveAgent(debug=False)
        self.agent.start_server()
        self.agent.initialize()
        self.source_path = os.path.abspath("src/webdemo/tmp/tmp.py")
        with open(self.source_path, "w") as f:
            f.write("")

    def restart(self):
        self.agent.stop_server()
        self.agent.start_server()
        self.agent.initialize()

    def check_if_parsable(self, code):
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
        is_parsable, changed = self.check_if_parsable(code)
        if not is_parsable:
            return
        if changed:
            with open(self.source_path, "w") as f:
                f.write(code)
            self.agent.load_code(self.source_path)
        return changed

    def execute(self, method, args):
        output = self.agent.execute(method, args)
        if output[0] == "Interrupted":
            self.agent.load_code(self.source_path)
        return self.construct_result_json(method, output, PythonPrettyPrinter) 
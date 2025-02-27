import os
import ast as python_ast
from ast import BinOp, Constant, NodeTransformer, Call, Add, fix_missing_locations
from livefromdap.agent.PythonLiveAgent import PythonLiveAgent
from livefromdap.agent.JavascriptLiveAgent import JavascriptLiveAgent
from prettyprinter.PythonPrettyPrinter import PythonPrettyPrinter
from .base import BaseAutoLiveAgent

class PolyglotJSRemap(NodeTransformer):
    js_agent: JavascriptLiveAgent

    def __init__(self, js_kaa):
        self.js_agent = js_kaa

    def visit_Call(self, node: Call):
        if python_ast.unparse(node.func) == "polyglot.eval":
            js_code = python_ast.unparse(node.args[1]).strip("'")
            result = int(
                self.js_agent.evaluate(js_code,
                                       self.js_agent.get_stackframes()[0]["id"])
                .get("body")
                .get("result") # type: ignore
                .strip("'"))
            return Constant(value=result)
        return node

class AutoPyJSAgent(BaseAutoLiveAgent):
    def __init__(self, raw=False):
        super().__init__(raw)
        self.agent = PythonLiveAgent(debug=False)
        self.js_agent = JavascriptLiveAgent(debug=False)
        self.agent.start_server()
        self.js_agent.start_server()
        self.agent.initialize()
        self.js_agent.initialize()
        self.source_path = os.path.abspath("src/webdemo/tmp/tmp.py")
        with open(self.source_path, "w") as f:
            f.write("")
        self.js_path = os.path.abspath("src/webdemo/tmp/tmpyjs.js")
        with open(self.js_path, "w") as f:
            f.write("")

    def restart(self):
        self.agent.stop_server()
        self.js_agent.stop_server()
        self.agent.start_server()
        self.js_agent.start_server()
        self.agent.initialize()
        self.js_agent.initialize()

    def check_if_parsable(self, code):
        parsable = False
        changed = False
        remapped_code = None
        try:
            ast = python_ast.parse(code)
            parsable = True
            remapped_code = python_ast.unparse(fix_missing_locations(PolyglotJSRemap(self.js_agent).visit(ast)))
        except Exception as e:
            return False, False, None

        if self.previous_ast is None:
            self.previous_ast = ast
            changed = True
        elif python_ast.dump(ast) != python_ast.dump(self.previous_ast):
            self.previous_ast = ast
            changed = True
        return parsable, changed, remapped_code

    def update_code(self, code):
        is_parsable, changed, remapped_code = self.check_if_parsable(code)
        if not is_parsable:
            return
        if remapped_code is not None:
            code = remapped_code
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
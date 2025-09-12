import os
import ast as python_ast
from livefromdap.agent.PyPolyglotLivExAgent import PyPolyglotLivExAgent
from livefromdap.agent.JSPolyglotLivExAgent import JSPolyglotLivExAgent
from prettyprinter.LivExPrettyPrinter import LivExPyPrettyPrinter, LivExJSPrettyPrinter
from tree_sitter import Language, Parser
from tree_sitter_javascript import language
from .base import BaseAutoLiveAgent

class AutoPolyLiveAgent(BaseAutoLiveAgent):
    def __init__(self, lang='python', raw=False):
        super().__init__(raw)
        if lang == 'python':
            self.agent = PyPolyglotLivExAgent(debug=False)
            self.source_path = os.path.abspath("src/webdemo/tmp/tmp.py")
        elif lang == 'javascript':
            self.agent = JSPolyglotLivExAgent(debug=False)
            self.source_path = os.path.abspath("src/webdemo/tmp/tmp.js")
            self.lang = Language(language())
            self.parser = Parser(self.lang)
        self.agent.start_server()
        self.agent.initialize()
        with open(self.source_path, "w") as f:
            f.write("")

    def restart(self):
        self.agent.stop_server()
        self.agent.start_server()
        self.agent.initialize()

    def check_if_parsable(self, code):
        if isinstance(self.agent, PyPolyglotLivExAgent):
            return self.check_if_parsable_py(code)
        elif isinstance(self.agent, JSPolyglotLivExAgent):
            return self.check_if_parsable_js(code)

    def check_if_parsable_py(self, code):
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

    def check_if_parsable_js(self, code):
        parsable = False
        changed = False
        try:
            ast = self.parser.parse(bytes(code, "utf8"))
            # Query to find ERROR or MISSING nodes
            query = self.lang.query("""
            (ERROR) @error
            """)
            captures = query.captures(ast.root_node)
            parsable = len(captures) == 0
        except Exception as e:
            return False, False

        if self.previous_ast is None:
            self.previous_ast = ast
            changed = True
        elif str(self.previous_ast.root_node) != str(ast.root_node):
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

    def execute(self, method, args, probes):
        output = self.agent.execute(method, args, probes)
        if output[0] == "Interrupted":
            self.agent.load_code(self.source_path)
        if isinstance(self.agent, PyPolyglotLivExAgent):
            return self.construct_result_json(method, output, LivExPyPrettyPrinter)
        elif isinstance(self.agent, JSPolyglotLivExAgent):
            return self.construct_result_json(method, output, LivExJSPrettyPrinter)
        
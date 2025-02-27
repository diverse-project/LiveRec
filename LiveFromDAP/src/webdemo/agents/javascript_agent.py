import os
from tree_sitter import Language, Parser
from tree_sitter_javascript import language
from livefromdap.agent.JavascriptLiveAgent import JavascriptLiveAgent
from prettyprinter.JavascriptPrettyPrinter import JavascriptPrettyPrinter
from .base import BaseAutoLiveAgent

class AutoJavascriptLiveAgent(BaseAutoLiveAgent):
    def __init__(self, raw=False):
        super().__init__(raw)
        self.agent = JavascriptLiveAgent(debug=False)
        self.agent.start_server()
        self.agent.initialize()
        self.source_path = os.path.abspath("src/webdemo/tmp/tmp.js")
        with open(self.source_path, "w") as f:
            f.write("")
        self.lang = Language(language())
        self.parser = Parser(self.lang)
    
    def restart(self):
        self.agent.stop_server()
        self.agent.start_server()
        self.agent.initialize()

    def check_if_parsable(self, code):
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

    def execute(self, method, args):
        output = self.agent.execute(self.source_path, method, args)
        if output is None:
            return ""
        if output[0] == "Interrupted":
            self.agent.load_code(self.source_path)
        return self.construct_result_json(method, output, JavascriptPrettyPrinter) 
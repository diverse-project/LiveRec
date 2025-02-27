import os
from tree_sitter import Language, Parser
from gopygo import parser as go_parser
from livefromdap.agent.GoLiveAgent import GoLiveAgent
from prettyprinter.GoPrettyPrinter import GoPrettyPrinter
from .base import BaseAutoLiveAgent

class AutoGoAgent(BaseAutoLiveAgent):
    def __init__(self, raw=False):
        super().__init__(raw)
        self.agent = GoLiveAgent(debug=False)
        self.agent.start_server()
        self.agent.initialize()
        self.source_path = os.path.abspath("src/webdemo/tmp/tmp.go")
        with open(self.source_path, "w") as f:
            f.write("")
        self.lang = Language(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "livefromdap", "bin", "treesitter", "go.so")),
            'go')
        self.parser = Parser()
        self.parser.set_language(self.lang)
        self.compiled_path = os.path.abspath("src/webdemo/tmp/tmp.so")

    def restart(self):
        self.agent.stop_server()
        self.agent.start_server()
        self.agent.initialize()

    def check_if_parsable(self, code):
        parsable = False
        changed = False
        try:
            ast = go_parser.parse(code)
            parsable = True
        except Exception as e:
            return False, False

        if self.previous_ast is None:
            self.previous_ast = ast
            changed = True
        elif ast != self.previous_ast:
            self.previous_ast = ast
            changed = True
        return parsable, changed

    def compile_go(self):
        command = f'go build -buildmode=plugin -gcflags="all=-N -l" -o {self.compiled_path} {self.source_path}'
        res = os.system(command)
        os.system(f"chmod +x {self.compiled_path}")
        return res

    def update_code(self, code):
        is_parsable, changed = self.check_if_parsable(code)
        if not is_parsable:
            return
        if changed:
            with open(self.source_path, "w") as f:
                f.write(code)
            if self.compile_go() != 0:
                return
            self.agent.load_code(self.compiled_path)
        return changed

    def execute(self, method, args):
        output = self.agent.execute(self.compiled_path, self.source_path, method, args)
        if output[0] == "Interrupted":
            self.agent.load_code(self.source_path)
        return self.construct_result_json(method, output, GoPrettyPrinter) 
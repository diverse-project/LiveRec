import os
from pycparser import c_parser, parse_file, c_generator
from livefromdap.agent.CLiveAgent import CLiveAgent
from prettyprinter.CPrettyPrinter import CPrettyPrinter
from .base import BaseAutoLiveAgent

class AutoCLiveAgent(BaseAutoLiveAgent):
    def __init__(self, raw=False):
        super().__init__(raw)
        self.agent = CLiveAgent(debug=False)
        self.agent.start_server()
        self.agent.initialize()
        self.buzy = False
        self.c_parser = c_parser.CParser()
        self.c_generator = c_generator.CGenerator()
        self.source_path = os.path.abspath("src/webdemo/tmp/tmp.c")
        with open(self.source_path, "w") as f:
            f.write("")
        self.compiled_path = os.path.abspath("src/webdemo/tmp/tmp.so")

    def restart(self):
        self.agent.stop_server()
        self.agent.start_server()
        self.agent.initialize()

    def check_if_parsable(self, code):
        parsable = False
        changed = False
        try:
            with open("src/webdemo/tmp/_tmp.c", "w") as f:
                f.write(code)
            ast = parse_file("src/webdemo/tmp/_tmp.c", use_cpp=True, parser=self.c_parser)
            parsable = True
        except Exception as e:
            return False, False

        if self.previous_ast is None:
            self.previous_ast = ast
            changed = True
        elif self.c_generator.visit(ast) != self.c_generator.visit(self.previous_ast):
            self.previous_ast = ast
            changed = True
        return parsable, changed

    def compile_c(self):
        command = f"gcc -g -fPIC -shared -o {self.compiled_path} {self.source_path}"
        res = os.system(command)
        return res

    def update_code(self, code):
        is_parsable, changed = self.check_if_parsable(code)
        if not is_parsable:
            return
        if changed:
            with open(self.source_path, "w") as f:
                f.write(code)
            if self.compile_c() != 0:
                return
            self.agent.load_code(self.compiled_path)
        return changed

    def execute(self, method, args):
        output = self.agent.execute(self.source_path, method, args)
        if output[0] == "Interrupted":
            self.agent.load_code(self.compiled_path)
        return self.construct_result_json(method, output, CPrettyPrinter) 
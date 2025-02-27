import json
import os
import javalang # type: ignore
from livefromdap.agent.JavaLiveAgent import JavaLiveAgent
from prettyprinter.JavaPrettyPrinter import JavaPrettyPrinter
from .base import BaseAutoLiveAgent

class AutoJavaLiveAgent(BaseAutoLiveAgent):
    def __init__(self, raw=False):
        super().__init__(raw)
        self.agent = JavaLiveAgent(debug=True)
        print("Starting server")
        self.agent.start_server()
        print("Initializing")
        self.agent.initialize()
        self.source_path = os.path.abspath("src/webdemo/tmp/Live.java")
        with open(self.source_path, "w") as f:
            f.write("")
        self.compiled_classpath = os.path.abspath("src/webdemo/tmp/")
        print("Finished object creation")

    def restart(self):
        self.agent.stop_server()
        self.agent.start_server()
        self.agent.initialize()

    def check_if_parsable(self, code):
        parsable = False
        changed = False
        try:
            ast = javalang.parse.parse(code)
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

    def compile_java(self):
        command = f"javac -g -d {self.compiled_classpath} {self.source_path}"
        res = os.system(command)
        return res

    def update_code(self, code):
        is_parsable, changed = self.check_if_parsable(code)
        if not is_parsable:
            return
        if changed:
            with open(self.source_path, "w") as f:
                f.write(code)
            if self.compile_java() != 0:
                return
            self.agent.load_code(self.compiled_classpath, "Live")
        return changed

    def execute(self, method, args):
        if "Live" not in self.agent.loaded_classes:
            self.agent.load_code(self.compiled_classpath, "Live")
        output = self.agent.execute("Live", method, args)
        if output[0] == "Interrupted":
            self.agent.load_code(self.compiled_classpath, "Live")
        return self.construct_result_json(method, output) 
    
    def construct_result_json(self, method, output):
        return_value, stacktrace = output
        if self.raw:
            stacktrace.last_stackframe.variables.append({"name":"return", "value":return_value})
            return json.dumps({
                "return_value": return_value,
                "stacktrace": stacktrace.to_json()
            })
        printer = JavaPrettyPrinter(self.source_path,"Live",method)
        output = printer.pretty_print(stacktrace, return_value=return_value)
        return output
    


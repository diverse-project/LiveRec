import os
import json
import subprocess
import javalang # type: ignore
from prettyprinter.JavaPrettyPrinter import JavaPrettyPrinter
from .base import BaseAutoLiveAgent

class AutoJavaJDILiveAgent(BaseAutoLiveAgent):
    def __init__(self, raw=False):
        super().__init__(raw)
        # Execute the agent from the directory where the jar is
        self.agent = subprocess.Popen(
            ["java -cp target/LiveProbes-1.0-jar-with-dependencies.jar debugger.LiveAgent"],
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "JavaProbes")),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True)
        # read the first line
        if self.agent.stdout is not None:
            self.agent.stdout.readline()
        self.source_path = os.path.abspath("src/webdemo/tmp/Live.java")
        with open(self.source_path, "w") as f:
            f.write("")
        self.compiled_classpath = os.path.abspath("src/webdemo/tmp/")

    def restart(self):
        pass

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
            payload = {
                "command": "loadClass",
                "params": {
                    "path": self.compiled_classpath,
                    "className": "Live"
                }
            }
            payload_str = json.dumps(payload) + "\n"
            assert self.agent.stdin is not None and self.agent.stdout is not None
            self.agent.stdin.write(payload_str.encode("utf8"))
            self.agent.stdin.flush()
            self.agent.stdout.readline()
        return changed

    def execute(self, method, args):
        payload = {
            "command": "evaluate",
            "params": {
                "method": method,
                "args": args
            }
        }
        payload_str = json.dumps(payload) + "\n"
        assert self.agent.stdin is not None and self.agent.stdout is not None
        self.agent.stdin.write(payload_str.encode("utf8"))
        self.agent.stdin.flush()
        line = self.agent.stdout.readline()
        response = json.loads(line.strip())
        return json.dumps({
            "return_value": response["result"],
            "stacktrace": response["stack"]
        }) 
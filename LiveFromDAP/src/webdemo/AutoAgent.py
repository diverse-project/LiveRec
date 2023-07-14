from abc import ABC, abstractmethod
import os
from threading import Thread

from livefromdap.agent.CLiveAgent import CLiveAgent
from livefromdap.agent.JavaLiveAgent import JavaLiveAgent
from livefromdap.agent.PythonLiveAgent import PythonLiveAgent
from prettyprinter.CPrettyPrinter import CPrettyPrinter
from pycparser import c_parser, parse_file, c_generator
import ast as python_ast
import javalang
from prettyprinter.JavaPrettyPrinter import JavaPrettyPrinter
from prettyprinter.PythonPrettyPrinter import PythonPrettyPrinter

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


class AutoLiveAgent(ABC):
    """Interface for the AutoLiveAgent
    This class define method for webdemo's agent"""

    @abstractmethod
    def update_code(self, code):
        """Update the code in the debuggee"""
        pass

    @abstractmethod
    def execute(self, method, args):
        """Execute the method in the debuggee"""
        pass

    @abstractmethod
    def restart(self):
        """Restart the debuggee"""
        pass

# @buzy decorator that check if the agent is buzy, and if not, execute the function in buzy mode
def buzy(func):
    def wrapper(self, *args, **kwargs):
        if self.buzy:
            return None
        self.buzy = True
        res = func(self, *args, **kwargs)
        self.buzy = False
        return res
    return wrapper


class AutoCLiveAgent(AutoLiveAgent):
    
    def __init__(self):
        self.agent = CLiveAgent(debug=True)
        self.agent.start_server()
        self.agent.initialize()
        print("Agent initialized")
        self.buzy = False
        self.c_parser = c_parser.CParser()
        self.c_generator = c_generator.CGenerator()
        self.previous_ast = None
        self.previous_exec_request = ""
        self.source_path = os.path.abspath("src/webdemo/tmp/tmp.c")
        with open(self.source_path, "w") as f:
            f.write("")
        self.compiled_path = os.path.abspath("src/webdemo/tmp/libtmp.so")

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
        

    def construct_result_json(self, method, output):
        return_value, stacktrace = output
        printer = CPrettyPrinter(self.source_path,method)
        output = printer.pretty_print(stacktrace, return_value=return_value['value'])
        return output

    def execute(self, method, args):
        thread = ThreadWithReturnValue(target=self.agent.execute, args=(self.source_path, method, args,))
        thread.start()
        # Wait for the thread to finish, with a timeout of 3 seconds
        output = thread.join(10)
        # If thread is still alive, it means it has timed out
        if thread.is_alive():
            raise TimeoutError
        # Get the output of the thread
        # Save the json result in a file
        return self.construct_result_json(method, output)
    

        

class AutoJavaLiveAgent(AutoLiveAgent):
    
    def __init__(self):
        self.buzy = True
        self.agent = JavaLiveAgent(debug=False)
        self.agent.start_server()
        self.agent.initialize()
        self.buzy = False
        self.source_path = os.path.abspath("src/webdemo/tmp/Live.java")
        with open(self.source_path, "w") as f:
            f.write("")
        self.compiled_classpath = os.path.abspath("src/webdemo/tmp/")
        self.previous_ast = None
    
    @buzy
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
    
    @buzy
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
        

    def construct_result_json(self, method, output):
        return_value, stacktrace = output
        printer = JavaPrettyPrinter(self.source_path,"Live",method)
        output = printer.pretty_print(stacktrace, return_value=return_value)
        return output

    @buzy
    def execute(self, method, args):
        if "Live" not in self.agent.loaded_classes:
            self.agent.load_code(self.compiled_classpath, "Live")
        thread = ThreadWithReturnValue(target=self.agent.execute, args=("Live", method, args,))
        thread.start()
        # Wait for the thread to finish, with a timeout of 3 seconds
        output = thread.join(10)
        # If thread is still alive, it means it has timed out
        if thread.is_alive():
            raise TimeoutError
        # Get the output of the thread
        # Save the json result in a file
        return self.construct_result_json(method, output)
    
class AutoPythonLiveAgent(AutoLiveAgent):
    
    def __init__(self):
        self.buzy = True
        self.agent = PythonLiveAgent(debug=False)
        self.agent.start_server()
        self.agent.initialize()
        self.buzy = False
        self.source_path = os.path.abspath("src/webdemo/tmp/tmp.py")
        with open(self.source_path, "w") as f:
            f.write("")
        self.previous_ast = None
    
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
    
    @buzy
    def update_code(self, code):
        is_parsable, changed = self.check_if_parsable(code)
        if not is_parsable:
            return
        if changed:
            with open(self.source_path, "w") as f:
                f.write(code)
            self.agent.load_code(self.source_path)

        return changed
        

    def construct_result_json(self, method, output):
        return_value, stacktrace = output
        printer = PythonPrettyPrinter(self.source_path,method)
        output = printer.pretty_print(stacktrace, return_value=return_value)
        return output

    @buzy
    def execute(self, method, args):
        thread = ThreadWithReturnValue(target=self.agent.execute, args=(method, args,))
        thread.start()
        # Wait for the thread to finish, with a timeout of 3 seconds
        output = thread.join(10)
        # If thread is still alive, it means it has timed out
        if thread.is_alive():
            raise TimeoutError
        # Get the output of the thread
        # Save the json result in a file
        return self.construct_result_json(method, output)


    

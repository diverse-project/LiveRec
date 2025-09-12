import os
from typing import override

from livefromdap.utils import StackRecording
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter
from tree_sitter_python import language as py_language
from tree_sitter_javascript import language as js_language



class LivExPyPrettyPrinter(TreeSitterPrettyPrinter):
    
    setup_function_query = """
        (function_definition
            name: (identifier) @fname
            (#match? @fname "{method}")
            parameters: (parameters 
                (identifier) @fparam
            )
        )@fdecl
    """
    
    assignment_query = """
        (assignment
            left: (identifier) @varname
        )
    """
    
    while_query = """
        (while_statement
            condition : (
                comparison_operator (
                    (identifier) @whileleft
                )
            )
        )
    """

    
    def __init__(self, file, method):
        self.language = py_language
        super().__init__(file, method) 
        

    @override
    def pretty_print(self, stacktrace : StackRecording, return_value=None):
        self.return_value = return_value
        self.stacktrace = stacktrace
        with open(self.file_path, "r") as f:
            code = f.read()
        self.ast = self.parser.parse(bytes(code, "utf8"))
        self.output = ["" for _ in range(len(code.split("\n")))]
        self.setup_function({"method": self.method_name})
        stacktrace.stackframes.pop(0)
        for stack in stacktrace.stackframes:
            self.output[stack.pos.line] += ";".join(["| " + varName + " = " + stack.get_variable(varName) + " " for varName in stack.get_variables()])
        # self.add_probes()
        return "\n".join(self.output)
    
class LivExJSPrettyPrinter(TreeSitterPrettyPrinter):

    setup_function_query = """
        (function_declaration 
            name: (identifier) @fname
            (#match? @fname "{method}")
            parameters: (formal_parameters
                (identifier) @fparam
            )
        ) @fdecl
    """
    
    assignment_query = """
        (variable_declarator
            name: (identifier) @varname
        )
        (assignment_expression
            left: (identifier) @assignleft
        )
    """
    
    while_query = """
        (while_statement
            condition : (
                parenthesized_expression (
                    binary_expression
                        left : (identifier)* @whileleft
                        right : (identifier)* @whileright
                )
            )
        )
    """

    def __init__(self, file, method):
        self.language = js_language
        super().__init__(file, method) 
        

    @override
    def pretty_print(self, stacktrace : StackRecording, return_value=None):
        self.return_value = return_value
        self.stacktrace = stacktrace
        with open(self.file_path, "r") as f:
            code = f.read()
        self.ast = self.parser.parse(bytes(code, "utf8"))
        self.output = ["" for _ in range(len(code.split("\n")))]
        self.setup_function({"method": self.method_name})
        stacktrace.stackframes.pop(0)
        for stack in stacktrace.stackframes:
            self.output[stack.pos.line] += ";".join(["| " + varName + " = " + stack.get_variable(varName) + " " for varName in stack.get_variables()])
        # self.add_probes()
        return "\n".join(self.output)
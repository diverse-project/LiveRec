from _ast import AugAssign, FunctionDef
import ast
from typing import Any

from livefromdap.utils.StackRecording import StackRecording


class PythonPrettyPrinter(ast.NodeVisitor):

    def __init__(self, file, method):
        self.file = file
        self.method = method
    
    def pretty_print(self, stacktrace : StackRecording, return_value=None):
        self.return_value = return_value
        self.stacktrace = stacktrace
        with open(self.file, "r") as f:
            code = f.read()
            self.ast = ast.parse(code)
        self.output = ["" for _ in range(len(code.split("\n")))]
        self.visit(self.ast)
        return "\n".join(self.output)

    
    def get_variable(self, line, variable_name):
        stackframes = self.stacktrace.get_stackframes_line(line)
        values = []
        for stackframe in stackframes:
            if stackframe.get_variable(variable_name) is not None:
                values.append(stackframe.get_variable(variable_name))
        return ",".join(values)
    
    def get_variable_after(self, line, variable_name):
        stackframes = self.stacktrace.get_stackframes_line(line)
        values = []
        for stackframe in stackframes:
            if stackframe.successor.get_variable(variable_name) is not None:
                values.append(stackframe.successor.get_variable(variable_name))
        return ",".join(values)
    
    def visit_FunctionDef(self, node: FunctionDef):
        if node.name == self.method:
            function_output = ""
            first_stackframe = self.stacktrace.stackframes[0]
            for arg in node.args.args:
                value = first_stackframe.get_variable(arg.arg)
                function_output += f"{arg.arg} = {value}, "
            if len(function_output) > 0:
                function_output = f"{node.name}({function_output[:-2]})"
                function_output += " -> "
            else:
                function_output = f"{node.name}() -> "

            if self.return_value is not None:
                function_output += self.return_value
            else:
                function_output += "None"
            self.output[node.lineno-1] = function_output
            self.generic_visit(node)

    def visit_Assign(self, node):
        output_assign = ""
        for target in node.targets:
            if isinstance(target, ast.Name):
                value = self.get_variable_after(target.lineno, target.id)
                if len(value) != 0:
                    output_assign += f"{target.id} = {value}, "
        if len(output_assign) != 0:
            output_assign = output_assign[:-2]
            self.output[node.lineno-1] = output_assign
        self.generic_visit(node)
        
    def visit_AugAssign(self, node: AugAssign):
        output_assign = ""
        if isinstance(node.target, ast.Name):
            value = self.get_variable_after(node.lineno, node.target.id)
            if len(value) != 0:
                output_assign += f"{node.target.id} = {value}"
        if len(output_assign) != 0:
            self.output[node.lineno-1] = output_assign
        self.generic_visit(node)
        

    def visit_While(self, node):
        vars = [node.test.left] + [n for n in node.test.comparators]
        while_output = ""
        for var in vars:
            if isinstance(var, ast.Name):
                value = self.get_variable(var.lineno, var.id)
                if len(value) != 0:
                    while_output += f"{var.id} = {value} | "
        if len(while_output) != 0:
            while_output = while_output[:-3]
            self.output[node.lineno-1] = while_output
        self.generic_visit(node)
        
    def visit_For(self, node):
        vars = [node.target]
        for_output = ""
        for var in vars:
            if isinstance(var, ast.Name):
                value = self.get_variable(var.lineno, var.id)
                if len(value) != 0:
                    for_output += f"{var.id} = {value} | "
        if len(for_output) != 0:
            for_output = for_output[:-3]
            self.output[node.lineno-1] = for_output
        self.generic_visit(node)
                
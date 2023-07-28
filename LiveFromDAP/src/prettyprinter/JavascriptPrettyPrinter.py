

import os
from tree_sitter import Language,Parser
from livefromdap.utils.StackRecording import StackRecording


class JavascriptPrettyPrinter():
    def __init__(self, file, method):
        self.file = file
        self.method = method
        self.lang = Language(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "livefromdap", "bin","treesitter","javascript.so")), 'javascript')
        self.parser = Parser()
        self.parser.set_language(self.lang)
        
    def pretty_print(self, stacktrace : StackRecording, return_value=None):
        self.return_value = return_value
        self.stacktrace = stacktrace
        with open(self.file, "r") as f:
            code = f.read()
        self.ast = self.parser.parse(bytes(code, "utf8"))
        self.output = ["" for _ in range(len(code.split("\n")))]
        self.visit()
        self.visit_assignment()
        self.visit_while()
        return "\n".join(self.output)

    def visit(self):
        function_params_query = self.lang.query("""
            (function_declaration 
                name: (identifier) @fname
                (#match? @fname "{method}")
                parameters: (formal_parameters
                    (identifier) @fparam
                )
            ) @fdecl
        """.format(method=self.method))
        captures = function_params_query.captures(self.ast.root_node)
        params = []
        for capture, capture_type in captures:
            if capture_type == "fdecl":
                self.function_start = capture.start_point
                self.function_end = capture.end_point
            elif capture_type == "fparam":
                params.append(capture.text.decode("utf8"))
                
        first_stackframe = self.stacktrace.stackframes[0]
        params_value = [first_stackframe.get_variable(p) for p in params]
        fdef_string = f"{self.method}({', '.join(params_value)}) -> {self.return_value}"
        self.output[self.function_start[0]] = fdef_string

        
    def is_in_range(self, node):
        return node.start_point[0] >= self.function_start[0] and node.end_point[0] <= self.function_end[0]
    
    def visit_assignment(self):
        vardecl_query = self.lang.query("""
            (variable_declarator
                name: (identifier) @varname
            )
            (assignment_expression
                left: (identifier) @assignleft
            )
        """)
        
        captures = vardecl_query.captures(self.ast.root_node)
        for capture, capture_type in captures:
            if self.is_in_range(capture):
                varname = capture.text.decode("utf8")
                value = ""
                for stack in self.stacktrace.get_stackframes_line(capture.start_point[0]+1):
                    if stack.successor is not None and stack.successor.get_variable(varname) is not None:
                        value += stack.successor.get_variable(varname) + ", "
                if value != "":
                    value = value[:-2]
                self.output[capture.start_point[0]] += f"{varname} = {value}"
    
    def visit_while(self):
        while_decl_query = self.lang.query("""
            (while_statement
                condition : (
                    parenthesized_expression (
                        binary_expression
                            left : (identifier)* @whileleft
                            right : (identifier)* @whileright
                    )
                )
            )
        """)
        captures = while_decl_query.captures(self.ast.root_node)
        variables = {}
        for capture, capture_type in captures:
            if self.is_in_range(capture):
                if capture_type == "whileleft" or capture_type == "whileright":
                    if not capture.start_point[0] in variables:
                        variables[capture.start_point[0]] = []
                    variables[capture.start_point[0]].append(capture.text.decode("utf8"))
        for line, vars in variables.items():
            stackframes = self.stacktrace.get_stackframes_line(line+1)
            output_string = ""
            for var in vars:
                output_string += f"{var} = {','.join([stack.successor.get_variable(var) for stack in stackframes])} | "
            self.output[line] += output_string[:-3]
               
        
        
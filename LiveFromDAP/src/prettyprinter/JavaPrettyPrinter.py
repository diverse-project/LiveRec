import os

from livefromdap.utils.StackRecording import StackRecording
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter

class JavaPrettyPrinter(TreeSitterPrettyPrinter):
    setup_function_query = """
        (class_declaration
            name: (identifier) @classname
            (#match? @classname "{class_name}")
            body: (class_body
                (method_declaration
                    name: (identifier) @fname
                    (#match? @fname "{method}")
                    parameters:(formal_parameters
                        (formal_parameter
                            name: (identifier)@fparam
                        )
                    )
                )@fdecl
            )
        )
    """
    
    assignment_query = """
        (local_variable_declaration
            declarator:(variable_declarator
                name: (identifier) @vardecl
            )
        )
        (assignment_expression
            left: (identifier) @varassign
        )
    """
    
    while_query = """
        (while_statement
            condition : (
                condition (
                    (binary_expression
                        left : (identifier)* @whileleft
                        right : (identifier)* @whileright
                    )
                )
            )
        )
    """
    
    def __init__(self, file, class_name, method):
        self.tree_sitter_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "livefromdap", "bin","treesitter","java.so"))
        self.tree_sitter_name = 'java'
        self.class_name = class_name
        super().__init__(file, method) 
    
    def pretty_print(self, stacktrace : StackRecording, return_value=None):
        self.stacktrace = stacktrace
        self.return_value = return_value
        with open(self.file_path, 'r') as f:
            code = f.read()
        self.ast = self.parser.parse(bytes(code, "utf8"))
        self.output = ["" for _ in range(len(code.split("\n")))]
        self.setup_function({"class_name": self.class_name, "method": self.method_name})
        self.add_probes()
        return "\n".join(self.output)

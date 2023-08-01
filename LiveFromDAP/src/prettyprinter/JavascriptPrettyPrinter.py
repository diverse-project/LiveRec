import os
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter

class JavascriptPrettyPrinter(TreeSitterPrettyPrinter):
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
        self.tree_sitter_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "livefromdap", "bin","treesitter","javascript.so"))
        self.tree_sitter_name = 'javascript'
        super().__init__(file, method) 
        
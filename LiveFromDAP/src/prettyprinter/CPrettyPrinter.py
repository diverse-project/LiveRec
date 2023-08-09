import os
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter

class CPrettyPrinter(TreeSitterPrettyPrinter):
    setup_function_query = """
        (function_definition
            (function_declarator 
                declarator: (identifier) @fname
                (#match? @fname "{method}")
                parameters: (parameter_list [
                    (parameter_declaration
                        declarator: (identifier) @fparam
                    )
                    (parameter_declaration
                        declarator: (array_declarator
                            declarator: (identifier) @fparam
                        ) 
                    )]
                )
            ) 
        )@fdecl
    """
    
    assignment_query = """
        (init_declarator
            declarator: (identifier) @varname
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
    
    for_query = """
        (for_statement
            initializer: (declaration
                declarator: (init_declarator
                declarator: (identifier) @forvar
                )
            )
            condition: (binary_expression
                left: (identifier) @forvar
                right: (identifier) @forvar
            )
            update: (update_expression
                argument: (identifier) @forvar
            )
        )
    """
    
    def __init__(self, file, method):
        self.tree_sitter_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "livefromdap", "bin","treesitter","c.so"))
        self.tree_sitter_name = 'c'
        super().__init__(file, method) 
        
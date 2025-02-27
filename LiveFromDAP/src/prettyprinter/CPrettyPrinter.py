import os
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter
from tree_sitter_c import language

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
        self.language = language
        super().__init__(file, method) 
        
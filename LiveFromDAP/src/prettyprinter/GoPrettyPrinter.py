import os
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter
from tree_sitter_go import language

class GoPrettyPrinter(TreeSitterPrettyPrinter):
    setup_function_query = """
        (function_declaration
            name: (identifier) @fname
            (#match? @fname "{method}")
            parameters: (parameter_list [
                (parameter_declaration
                    name: (identifier) @fparam
                )
            ])
        )@fdecl
    """

    assignment_query = """
        (short_var_declaration
            left: (expression_list
                (identifier) @varname
            )
        )
        (assignment_statement
            left: (expression_list
                (identifier) @assignleft
            )
        )
    """

    def __init__(self, file, method):
        self.language = language
        super().__init__(file, method)

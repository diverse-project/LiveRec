import os
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter

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
        self.tree_sitter_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "livefromdap", "bin", "treesitter", "go.so"))
        self.tree_sitter_name = 'go'
        super().__init__(file, method)

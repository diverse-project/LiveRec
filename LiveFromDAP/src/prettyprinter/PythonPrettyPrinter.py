import os
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter

class PythonPrettyPrinter(TreeSitterPrettyPrinter):
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
        self.tree_sitter_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "livefromdap", "bin","treesitter","python.so"))
        self.tree_sitter_name = 'python'
        super().__init__(file, method) 
        
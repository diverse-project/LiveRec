import os
from .TreeSitterPrettyPrinter import TreeSitterPrettyPrinter
from tree_sitter_python import language

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
        self.language = language
        super().__init__(file, method) 
        
from tree_sitter import Language,Parser
from livefromdap.utils.StackRecording import StackRecording

class TreeSitterPrettyPrinter():
    tree_sitter_path : str
    tree_sitter_name : str
    
    def __init__(self, file_path, method_name):
        self.file_path = file_path
        self.method_name = method_name
        #check if tree_sitter_path has been set by a child class
        if not hasattr(self, "tree_sitter_path") or not hasattr(self, "tree_sitter_name"):
            raise Exception("tree_sitter_path and tree_sitter_name must be set by child class")
    
        if not hasattr(self, "setup_function_query"):
            raise Exception(f"setup_function_query must be set by child class")
        self.lang = Language(self.tree_sitter_path, self.tree_sitter_name)
        self.parser = Parser()
        self.parser.set_language(self.lang)
        
    def pretty_print(self, stacktrace : StackRecording, return_value=None):
        self.return_value = return_value
        self.stacktrace = stacktrace
        with open(self.file_path, "r") as f:
            code = f.read()
        self.ast = self.parser.parse(bytes(code, "utf8"))
        self.output = ["" for _ in range(len(code.split("\n")))]
        self.setup_function({"method": self.method_name})
        self.add_probes()
        return "\n".join(self.output)
    
    def add_probes(self):
        if hasattr(self, "assignment_query"):
            self.visit_assignment()
        if hasattr(self, "while_query"):
            self.visit_while()
        if hasattr(self, "for_query"):
            self.visit_for()
    
    def is_in_range(self, node):
        return node.start_point[0] >= self.function_start[0] and node.end_point[0] <= self.function_end[0]
    
    
    def setup_function(self, formatter : dict):
        function_params_query = self.lang.query(self.setup_function_query.format(**formatter)) # type: ignore
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
        fdef_string = f"{self.method_name}({', '.join(params_value)}) -> {self.return_value}"
        self.output[self.function_start[0]] = fdef_string
        
    def visit_assignment(self):
        vardecl_query = self.lang.query(self.assignment_query) # type: ignore
        
        captures = vardecl_query.captures(self.ast.root_node)
        for capture, _ in captures:
            if self.is_in_range(capture):
                varname = capture.text.decode("utf8")
                value = ""
                for stack in self.stacktrace.get_stackframes_line(capture.start_point[0]+1):
                    if stack.successor is not None and len(stack.successor.get_variable(varname)) > 0:
                        value += stack.successor.get_variable(varname) + ", "
                if value != "":
                    value = value[:-2]
                self.output[capture.start_point[0]] += f"{varname} = {value}"
    
    def visit_while(self):
        while_decl_query = self.lang.query(self.while_query) # type: ignore
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
                output_string += f"{var} = {','.join([stack.successor.get_variable(var) for stack in stackframes if stack.successor is not None])} | "
            self.output[line] += output_string[:-3]
    
    def visit_for(self):
        for_decl_query = self.lang.query(self.for_query) # type: ignore
        captures = for_decl_query.captures(self.ast.root_node)
        variables = {}
        for capture, capture_type in captures:
            if self.is_in_range(capture):
                if capture_type == "forvar":
                    if not capture.start_point[0] in variables:
                        variables[capture.start_point[0]] = []
                    variables[capture.start_point[0]].append(capture.text.decode("utf8").strip())
        for line, vars in variables.items():
            stackframes = self.stacktrace.get_stackframes_line(line+1)
            output_string = ""
            for var in set(vars):
                output_string += f"{var} = {','.join([stack.successor.get_variable(var) for stack in stackframes if stack.successor is not None])} | "
            self.output[line] = output_string[:-3]
        
    
from tree_sitter import Language, Node,Parser
from livefromdap.utils.StackRecording import StackRecording

class TreeSitterPrettyPrinter():
    language : object
    
    def __init__(self, file_path, method_name):
        self.file_path = file_path
        self.method_name = method_name
        if not hasattr(self, "language"):
            raise Exception(f"language must be set by child class")

        if not hasattr(self, "setup_function_query"):
            raise Exception(f"setup_function_query must be set by child class")
        self.lang = Language(self.language()) # type: ignore
        self.parser = Parser(self.lang)
        
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
    
    def is_in_range(self, node : Node):
        return node.start_point[0] >= self.function_start[0] and node.end_point[0] <= self.function_end[0]
    
    
    def setup_function(self, formatter : dict):
        function_params_query = self.lang.query(self.setup_function_query.format(**formatter)) # type: ignore
        captures = function_params_query.captures(self.ast.root_node)
        params = []
        for capture_type, capture in captures.items():
            if capture_type == "fdecl":
                self.function_start = capture[0].start_point
                self.function_end = capture[0].end_point
            elif capture_type == "fparam":
                for c in capture:
                    if c.text is not None:
                        params.append(c.text.decode("utf8"))
                
        first_stackframe = self.stacktrace.stackframes[0]
        params_value = [first_stackframe.get_variable(p) for p in params]
        fdef_string = f"{self.method_name}({', '.join(params_value)}) -> {self.return_value}"
        self.output[self.function_start[0]] = fdef_string
        
    def visit_assignment(self):
        vardecl_query = self.lang.query(self.assignment_query) # type: ignore
        
        captures = vardecl_query.captures(self.ast.root_node)
        all_captures = [node for capture in captures.values() for node in capture]
        for capture in all_captures:
            if self.is_in_range(capture) and capture.text is not None:
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
        all_captures = [(node, capture_type) for capture_type,capture in captures.items() for node in capture]
        for capture, capture_type in all_captures:
            if self.is_in_range(capture):
                if capture_type == "whileleft" or capture_type == "whileright":
                    if not capture.start_point[0] in variables:
                        variables[capture.start_point[0]] = []
                    if capture.text is not None:
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
        all_captures = [(node, capture_type) for capture_type,capture in captures.items() for node in capture]  
        for capture, capture_type in all_captures:
            if self.is_in_range(capture):
                if capture_type == "forvar":
                    if not capture.start_point[0] in variables:
                        variables[capture.start_point[0]] = []
                    if capture.text is not None:
                        variables[capture.start_point[0]].append(capture.text.decode("utf8").strip())
        for line, vars in variables.items():
            stackframes = self.stacktrace.get_stackframes_line(line+1)
            output_string = ""
            for var in set(vars):
                output_string += f"{var} = {','.join([stack.successor.get_variable(var) for stack in stackframes if stack.successor is not None])} | "
            self.output[line] = output_string[:-3]
        
    
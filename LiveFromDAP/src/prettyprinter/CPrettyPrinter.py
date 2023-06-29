from pycparser import c_ast, parse_file

from livefromdap.utils.StackRecord import StackRecord


class CPrettyPrinter(c_ast.NodeVisitor):

    def __init__(self, target_path, method):
        self.target_path = target_path
        self.filename = target_path.split("/")[-1]
        self.method = method
        self.changed_source = False
        # Get the number of lines in the file
    
    def pretty_print(self, stacktrace : StackRecord, return_value=None):
        self.return_value = return_value
        self.stacktrace = stacktrace
        self.ast = parse_file(self.target_path, use_cpp=True)
        self._visit_ast(self.ast)
        self.ast = None
        self.return_value = None
        self.stacktrace = None
        return "\n".join(self.output)
    
    def _visit_ast(self, ast):
        with open(self.target_path, "r") as f:
            self.lines = f.readlines()
        self.output = ["" for _ in range(len(self.lines))]
        self.visit(ast)

    
    def get_variable(self, line, variable_name):
        stackframes = self.stacktrace.get_stackframes_line(line)
        values = []
        for stackframe in stackframes:
            if (value:=stackframe.get_variable(variable_name)) is not None:
                    values.append(value)
        return values
                
    def visit_FuncDecl(self, node):
        if node.type.declname == self.method:
            params_names = [param.name for param in node.args.params]
            # We need to get the correct stackframe
            # we need to add at the decl position in out something like:
            # params1= ...; params2= ...; params3= ...; -> return_value= ...
            string_output = ""
            for param in params_names:
                string_output += f"{param}={self.get_variable(node.type.coord.line+1,param)[0]}; "
            string_output += f"-> return_value={self.return_value}"
            self.output[node.type.coord.line-1] = string_output
    
    def visit_FuncDef(self, node):
        if node.decl.name == self.method:
            self.generic_visit(node)
            return

    def visit_Decl(self, node):
        if isinstance(node.type, c_ast.FuncDecl):
            self.generic_visit(node)
            return
        output_string = f"{node.name}= "
        for stackframe in self.stacktrace.get_stackframes_line(node.coord.line):
            if (value:=stackframe.successor.get_variable(node.name)) is not None:
                output_string += f"{value} | "
        self.output[node.coord.line-1] = output_string[:-2]

    def visit_Assignment(self, node):
        output_string = f"{node.lvalue.name}= "
        for stackframe in self.stacktrace.get_stackframes_line(node.coord.line):
            if (value:=stackframe.successor.get_variable(node.lvalue.name)) is not None:
                output_string += f"{value} | "
        if output_string != f"{node.lvalue.name}= ":
            self.output[node.coord.line-1] = output_string[:-2]

    def visit_While(self, node):
        cond = node.cond
        # We need to add a empty line after the while in the source code if there is none
        with open(self.target_path, "r") as f:
            code = f.readlines()
        if code[node.coord.line] != "\n":
            code.insert(node.coord.line, "\n")
            with open(self.target_path, "w") as f:
                f.writelines(code)
            self.changed_source = True
            self.stacktrace.shift_line(node.coord.line, 1)
            self._visit_ast(self.ast)
            return
        # check if left is a variable
        if isinstance(cond.left, c_ast.ID):
            output_string = f"{cond.left.name}= "
            for stackframe in self.stacktrace.get_stackframes_line(node.coord.line):
                if (value:=stackframe.get_variable(cond.left.name)) is not None:
                    output_string += f"{value} | "
            if output_string != f"{cond.left.name}= ":
                self.output[node.coord.line-1] = output_string[:-2]
        # check if right is a variable
        if isinstance(cond.right, c_ast.ID):
            output_string = f"{cond.right.name}= "
            for stackframe in self.stacktrace.get_stackframes_line(node.coord.line):
                if (value:=stackframe.get_variable(cond.right.name)) is not None:
                    output_string += f"{value} | "
            if output_string != f"{cond.right.name}= ":
                self.output[node.coord.line] = output_string[:-2]

        # TODO extend this to all the content of while loop
        if isinstance(cond.left, c_ast.ID) and isinstance(cond.right, c_ast.ID):
            data = [self.output[node.coord.line-1], self.output[node.coord.line]]
            max_length = max(len(item.split('=')[0]) for item in data)
            # Print the formatted output
            data_corrected = []
            for item in data:
                variable, value = item.split('=')
                output = "{:<{width}} = {}".format(variable.strip(), value.strip(), width=max_length)
                data_corrected.append(output)
            self.output[node.coord.line-1] = data_corrected[0]
            self.output[node.coord.line] = data_corrected[1]
        self.generic_visit(node)

import javalang
from javalang.visitor import JavaVisitor
from livefromdap.utils.StackRecording import StackRecording

class JavaPrettyPrinter(JavaVisitor):
    def __init__(self, file, class_name, method_name):
        self.file = file
        self.class_name = class_name
        self.method_name = method_name
        self.eval_op = None

    def pretty_print(self, stacktrace : StackRecording, return_value=None):
        self.stacktrace = stacktrace
        self.return_value = return_value
        with open(self.file, 'r') as f:
            code = f.read()
            self.tree = javalang.parse.parse(code)
            self.output = ["" for _ in range(len(code.split("\n")))]
        self.visit(self.tree)
        return "\n".join(self.output)

    def get_variable(self, line, variable_name):
        stackframes = self.stacktrace.get_stackframes_line(line)
        values = []
        for stackframe in stackframes:
            if stackframe.get_variable(variable_name) is not None:
                values.append(stackframe.get_variable(variable_name))
        return ",".join(values)
    
    def get_variable_after(self, line, variable_name):
        stackframes = self.stacktrace.get_stackframes_line(line)
        values = []
        for stackframe in stackframes:
            if stackframe.successor.get_variable(variable_name) is not None:
                values.append(stackframe.successor.get_variable(variable_name))
        return ",".join(values)

    def visit_ClassDeclaration(self, node):
        if self.class_name is None or node.name == self.class_name:
            self.generic_visit(node)

    def visit_MethodDeclaration(self, node):
        if self.method_name is None or node.name == self.method_name:
            method_output = ""
            first_stackframe = self.stacktrace.stackframes[0]
            for parameter in node.parameters:
                value = first_stackframe.get_variable(parameter.name)
                method_output += f"{parameter.name} = {value}, "
            method_output = method_output[:-2]
            method_output += " -> "
            if self.return_value is not None:
                method_output += self.return_value
            self.output[node.position.line-1] = method_output
            self.generic_visit(node)

    def visit_LocalVariableDeclaration(self, node):
        value = self.get_variable_after(node.position.line, node.declarators[0].name)
        if len(value) != 0:
            self.output[node.position.line-1] = f"{node.declarators[0].name} = {value}"
        self.generic_visit(node)

    def visit_StatementExpression(self, node):
        if isinstance(node.expression, javalang.tree.Assignment):
            value = self.get_variable(node.position.line, node.expression.expressionl.member)
            if len(value) != 0:
                self.output[node.position.line-1] = f"{node.expression.expressionl.member} = {value}"
        self.generic_visit(node)

    def visit_WhileStatement(self, node):
        self.eval_op = node.position
        self.visit(node.condition)
        self.eval_op = None
        self.generic_visit(node)

    def visit_BinaryOperation(self, node):
        if self.eval_op is not None:
            while_output = ""
            if isinstance(node.operandl, javalang.tree.MemberReference):
                value = self.get_variable(self.eval_op.line, node.operandl.member)
                if len(value) != 0:
                    while_output += f"{node.operandl.member} = {value} | "
            if isinstance(node.operandr, javalang.tree.MemberReference):
                value = self.get_variable(self.eval_op.line, node.operandr.member)
                if len(value) != 0:
                    while_output += f"{node.operandr.member} = {value}"
            if len(while_output) != 0:
                self.output[self.eval_op.line-1] = while_output
        self.generic_visit(node)

        

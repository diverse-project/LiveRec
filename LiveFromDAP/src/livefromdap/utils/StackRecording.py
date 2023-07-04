class Stackframe():
    line : int
    variables : list
    predecessor : "Stackframe"
    successor : "Stackframe"

    def __init__(self, line, variables):
        self.line = line   
        self.variables = variables
        self.predecessor = None
        self.successor = None

    def set_predecessor(self, predecessor):
        self.predecessor = predecessor
    
    def set_successor(self, successor):
        self.successor = successor

    def get_variable(self):
        return [v["name"] for v in self.variables]

    def get_variable(self, name):
        for v in self.variables:
            if v["name"] == name:
                return v["value"]

class StackRecording():
    stackframes : list
    last_stackframe : Stackframe
    
    def __init__(self):
        self.stackframes = []
        self.last_stackframe = None

    def add_stackframe(self, stackframe: Stackframe):
        if not self.last_stackframe is None:
            self.last_stackframe.set_successor(stackframe)
            stackframe.set_predecessor(self.last_stackframe)
        self.stackframes.append(stackframe)
        self.last_stackframe = stackframe

    def get_stackframes_line(self, line):
        return [s for s in self.stackframes if s.line == line]
    
    def shift_line(self, line, shift):
        for s in self.stackframes:
            if s.line > line:
                s.line += shift
    


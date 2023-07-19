class Position():
    line : int
    column : int

    def __init__(self, line, column):
        self.line = line
        self.column = column

    def to_json(self):
        return {
            "line": self.line,
            "column": self.column
        }



class Stackframe():
    pos : Position
    height : int
    variables : list
    predecessor : "Stackframe"
    successor : "Stackframe"

    def __init__(self, line, column, height, variables):
        self.pos = Position(line, column)
        self.height = height
        self.variables = variables
        self.predecessor = None
        self.successor = None

    def set_predecessor(self, predecessor):
        self.predecessor = predecessor
    
    def set_successor(self, successor):
        self.successor = successor

    def get_variables(self):
        return [v["name"] for v in self.variables]

    def get_variable(self, name):
        for v in self.variables:
            if v["name"] == name:
                return v["value"]

    def get_type(self, name):
        for v in self.variables:
            if v["name"] == name:
                return v["type"]
            
    def to_json(self):
        return {
            "id": id(self),
            "pos": self.pos.to_json(),
            "height": self.height,
            "variables": self.variables,
            "predecessor": id(self.predecessor),
            "successor": id(self.successor)
        }

class StackRecording():
    stackframes : list
    last_stackframe : Stackframe
    
    def __init__(self):
        self.stackframes = []
        self.last_stackframe = None
        
    def __len__(self):
        return len(self.stackframes)

    def add_stackframe(self, stackframe: Stackframe):
        if not self.last_stackframe is None:
            self.last_stackframe.set_successor(stackframe)
            stackframe.set_predecessor(self.last_stackframe)
        self.stackframes.append(stackframe)
        self.last_stackframe = stackframe

    def get_stackframes_line(self, line):
        return [s for s in self.stackframes if s.pos.line == line]
    
    def shift_line(self, line, shift):
        for s in self.stackframes:
            if s.pos.line > line:
                s.pos.line += shift

    def to_json(self):
        return [s.to_json() for s in self.stackframes]
    


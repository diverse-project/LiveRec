class ChangeRecording:
    def __init__(self, stack_recording):
        self.stack_recording = stack_recording
        self.history = {}
        self.process()
        
    def process(self):
        actual_variables = {}
        stackframe = self.stack_recording.stackframes[0]
        self.history[stackframe.pos.line] = []
        for variable in stackframe.get_variables():
            self.history[stackframe.pos.line].append((variable, stackframe.get_variable(variable)))
            actual_variables[variable] = stackframe.get_variable(variable)
        
        for i, stackframe in enumerate(self.stack_recording.stackframes[1:]):
            if not stackframe.pos.line in self.history:
                self.history[stackframe.pos.line] = []
            for variable in stackframe.get_variables():
                if variable not in actual_variables or actual_variables[variable] != stackframe.get_variable(variable):
                    line = self.stack_recording.stackframes[i-1].pos.line
                    actual_variables[variable] = stackframe.get_variable(variable)
                    self.history[line].append((variable, stackframe.get_variable(variable)))
            
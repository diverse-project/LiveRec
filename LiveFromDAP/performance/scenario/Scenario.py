

import os


class Scenario:
    
    def __init__(self, directory, lang, extension, target):
        self.directory = directory
        self.lang = lang
        self.extension = extension
        self.target = target
        with open(os.path.abspath(self.target), 'w') as file:
            file.write('')
        self.index = -1
    
    def get_current_info(self):
        with open(os.path.join(self.directory,self.lang,str(self.index)+self.extension)) as file:
            lines = file.read().split('\n')
        code = "\n".join(lines[1:])
        with open(os.path.abspath(self.target), 'w') as file:
            file.write(code)
        return lines[0].split(';')
    
    def __iter__(self):
        return self
        
    
    def __next__(self):
        self.index += 1
        try:
            return self.get_current_info()
        except FileNotFoundError as e:
            self.index = 0
            with open(os.path.abspath(self.target), 'w') as file:
                file.write('')
            raise StopIteration
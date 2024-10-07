from livefromdap.polyglot_dap.PolyglotDebugAgent import PolyglotDebugAgent
import json


debugger = PolyglotDebugAgent()

# debugger.start_server()
# debugger.initialize()

class FakeDict:

    def __init__(self, dict):
        self.dct = dict

    def __str__(self) -> str:
        return json.dumps(self.dct)
    
    __repr__ = __str__

# file = input("Please enter the starting file to debug: ")
# debugger.load_code(file)

def jsonifydict(d):
    if isinstance(d, dict):
        return FakeDict(d)
    elif isinstance(d, list):
        return [jsonifydict(x) for x in d]
    else:
        return d

while True:
    result = eval(input())
    result = jsonifydict(result)
    print(result, flush=True)
    # print("Debugger stopped at:", debugger.get_stackframes()[0])
    # command = input()
    # if command.startswith("breakpoint"):
    #     args = command.split(" ")
    #     print(f"Set breakpoint at line {args[2]} for file {args[1]}")
    #     debugger.set_breakpoint(args[1], [int(args[2])])
    # elif command == "continue":
    #     debugger.next_breakpoint()
    # elif command == "reload":
    #     arg = command.split(" ")
    #     debugger.load_code(args[1])
    # elif command == "quit" or command == "q":
    #     exit()
    # else:
    #     print("Unrecognized command; please input either 'breakpoint <file> <line>', 'continue' or 'quit'")
        
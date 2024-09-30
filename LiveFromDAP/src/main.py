from livefromdap.polyglot_dap.PolyglotDebugAgent import PolyglotDebugAgent


debugger = PolyglotDebugAgent()

debugger.start_server()
debugger.initialize()


    
file = input("Please enter the starting file to debug: ")
debugger.load_code(file)

while True:
    print("Debugger stopped at:", debugger.get_stackframes()[0])
    command = input()
    if command.startswith("breakpoint"):
        args = command.split(" ")
        print(f"Set breakpoint at line {args[2]} for file {args[1]}")
        debugger.set_breakpoint(args[1], [int(args[2])])
    elif command == "continue":
        debugger.next_breakpoint()
    elif command == "reload":
        arg = command.split(" ")
        debugger.load_code(args[1])
    elif command == "quit" or command == "q":
        exit()
    else:
        print("Unrecognized command; please input either 'breakpoint <file> <line>', 'continue' or 'quit'")
        
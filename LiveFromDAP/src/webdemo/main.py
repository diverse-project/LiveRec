from threading import Thread
from flask import Flask, render_template
from flask_socketio import SocketIO, send
from livefromdap.agent.CLiveAgent import CLiveAgent
import json
import os
from prettyprinter.CPrettyPrinter import CPrettyPrinter
from pycparser import c_parser, parse_file, c_generator

parser = c_parser.CParser()
generator = c_generator.CGenerator()
previous_ast = None
previous_exec_request = ""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
agent = CLiveAgent(debug=False)
source_path = os.path.abspath("src/webdemo/tmp/tmp.c")
compiled_path = os.path.abspath("src/webdemo/tmp/libtmp.so")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('json')
def handle_json(json_msg):
    global previous_exec_request
    json_dict = json_msg
    if json_dict["event"] == "codeChange":
        is_parsable, changed, reason = check_if_parsable(json_dict["code"])
        code = json_dict["code"]
        if not is_parsable:
            send_status("Syntax error : " + reason)
            return
        if changed:
            with open(source_path, "w") as f:
                f.write(code)
            if compile_c() != 0:
                send_status("Compilation error")
                return
            send_status("Code changed, loading...")
            agent.load_code(compiled_path)
        # We need to find if there is line that start with //@
        for line in code.split("\n"):
            if line.startswith("//@"):
                exec_request = line[3:].strip()
                if exec_request != previous_exec_request or changed:
                    previous_exec_request = exec_request
                    if "(" in exec_request and exec_request.endswith(")"):
                        method = exec_request.split("(")[0]
                        args = exec_request.split("(")[1][:-1].split(",")
                        if not "" in map(lambda x: x.strip(), args):
                            response = execute_method(method, args)
                            send(response, json=True)
    if json_dict["event"] == "init":
        init()

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return



def check_if_parsable(code):
    global parser, previous_ast, generator
    parsable = False
    changed = False
    try:
        with open("src/webdemo/tmp/_tmp.c", "w") as f:
            f.write(code)
        ast = parse_file("src/webdemo/tmp/_tmp.c", use_cpp=True, parser=parser)
        parsable = True
    except Exception as e:
        return False, False, str(e).replace('src/webdemo/tmp/_tmp.c', 'line')
    if previous_ast is None:
        previous_ast = ast
        changed = True
    elif generator.visit(ast) != generator.visit(previous_ast):
        previous_ast = ast
        changed = True
    return parsable, changed, ""

def execute_method(method, args):
    #Create a thread to execute the method
    thread = ThreadWithReturnValue(target=agent.execute, args=(source_path, method, args,))
    thread.start()
    # Wait for the thread to finish, with a timeout of 3 seconds
    output = thread.join(3)
    # If thread is still alive, it means it has timed out
    if thread.is_alive():
        print("Timeout")
        agent.stop_server()
        init(keep_old=True)
        return {
            "event": "executeTimeout"
        }
    # Get the output of the thread
    # Save the json result in a file
    construct_result = construct_result_json(method, output)
    response = {
        "event": "executeOutput",
        "output": construct_result
    }
    return response
    


def construct_result_json(method, output):
    return_value, stacktrace = output
    printer = CPrettyPrinter(source_path,method)
    output = printer.pretty_print(stacktrace, return_value=return_value['value'])
    if printer.changed_source:
        with open(source_path, "r") as f:
            code = f.read()
        req = {
            "event": "codeChange",
            "code": code
        }
        send(req, json=True)
    return output
    

def compile_c():
    command = "gcc -g -fPIC -shared -o src/webdemo/tmp/libtmp.so src/webdemo/tmp/tmp.c"
    res = os.system(command)
    return res


def send_status(status, **kwargs):
    req = {
        "event": "status",
        "status": status,
        **kwargs
    }
    send(req, json=True)

def init(keep_old=False):
    send_status("Initializing Agent...")
    if not keep_old:
        with open(source_path, "w") as f:
            f.write("")
    agent.start_server()
    agent.initialize()
    send_status("Agent initialized")

if __name__ == '__main__':
    socketio.run(app, debug=True)
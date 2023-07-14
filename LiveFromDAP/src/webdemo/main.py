from queue import Queue
from threading import Thread
import time
import uuid
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room
from webdemo.AutoAgent import AutoCLiveAgent, AutoJavaLiveAgent, AutoPythonLiveAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
sessions = {}

sessions_to_sid = {}

def create_agent(language):
    if language == "c":
        return AutoCLiveAgent()
    elif language == "java":
        return AutoJavaLiveAgent()
    elif language == "python":
        return AutoPythonLiveAgent()
    else:
        raise NotImplementedError() # TODO implement other languages


def clean_code(code):
    return "\n".join(["" if line.strip().startswith("!!!") else line for line in code.split("\n") ])

def extract_exec_request(code):
    for line in code.split("\n"):
        line = line.strip()
        if line.startswith("!!!"):
            exec_request = line[3:].strip()
            if "(" in exec_request and exec_request.endswith(")"):
                method = exec_request.split("(")[0]
                args = exec_request.split("(")[1][:-1].split(",")
                if not "" in map(lambda x: x.strip(), args):
                    return method, args
    return None

class Session():
    """A session is a unique identifier for a user. 
    It host the auto agent and the code of the user
    It has a queue of requests to execute and a thread that executes them
    """

    def __init__(self, room, socketio, language):
        self.room = room
        self.socketio = socketio
        self.language = language
        self.agent = create_agent(language)
        self.code = ""
        self.queue = Queue()
        self.last_execution_line = None
        self.thread = Thread(target=self.event_loop, daemon=True)
        self.thread.start()

    def event_loop(self):
        while True:
            # Wait for a request to execute
            request = self.queue.get()
            # If the request is None, it means the session is closed
            if request is None:
                break
            # If the request is not None, execute it
            self.handle_request(request)
            # Notify the queue that the request is done
            self.queue.task_done()
    
    def handle_request(self, request):
        if request["event"] == "codeChange":
            session_id = request["session_id"]
            code = clean_code(request["code"])
            changed = self.agent.update_code(code)
            
            self.send_status("codeChange", session_id=session_id)

            exec_req = extract_exec_request(request["code"])

            if exec_req is not None:

                if changed or exec_req != self.last_execution_line:
                    result = self.agent.execute(*exec_req)
                    self.send({
                        "event": "executeOutput",
                        "output": result,
                    }, json=True)
                    self.last_execution_line = exec_req
            self.send_status("ready", session_id=session_id)
        elif request["event"] == "initialize":
            session_id = request["session_id"]
            self.send_status("agent_up", session_id=session_id)

    def send(self, data, **kwargs):
        self.socketio.send(data, to=self.room, **kwargs)

    def send_status(self, status, **kwargs):
        req = {
            "event": "status",
            "status": status,
            **kwargs
        }
        self.send(req, json=True)
        


# Start the agent with a language parameter
@app.route('/dap/<language>')
def dap(language):
    # create a unique session id
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(session_id, socketio, language)
    return render_template('dap.html', language=language, session_id=session_id)

@socketio.on('disconnect')
def on_disconnect(*args, **kwargs):
    if request.sid in sessions_to_sid:
        session_id = sessions_to_sid[request.sid]
        sessions[session_id].agent.agent.stop_server()
        del sessions[session_id]

@socketio.on('join')
def on_join(data):
    session_id = data.get("session_id")
    sessions_to_sid[request.sid] = session_id
    language = data.get("language")
    join_room(session_id)
    if session_id in sessions:
        sessions[session_id].send_status("agent_up", session_id=session_id)
    else:
        sessions[session_id] = Session(session_id, socketio, language)


@socketio.on('json')
def handle_json(json_msg):
    session_id = json_msg.get("session_id")
    if session_id is None:
        return
    sessions[session_id].queue.put(json_msg)
    
        


if __name__ == '__main__':
    #no reload because of the global variables
    socketio.run(app)
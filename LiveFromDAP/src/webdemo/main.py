import json
from queue import Queue
import re
from threading import Thread
import time
import uuid
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, send
from webdemo.AutoAgent import AutoCLiveAgent, AutoExecutionAgent, AutoJavaLiveAgent, AutoPyJSDynamicAgent, \
    AutoPythonLiveAgent, AutoJavascriptLiveAgent, AutoJavaJDILiveAgent, AutoPyJSAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
sessions = {}

sessions_to_sid = {}


def create_agent(language, raw=False):
    if language == "c":
        return AutoCLiveAgent(raw=raw)
    elif language == "java":
        return AutoJavaLiveAgent(raw=raw)
    elif language == "python":
        return AutoPythonLiveAgent(raw=raw)
    elif language == "javascript":
        return AutoJavascriptLiveAgent(raw=raw)
    elif language == "pyjs":
        return AutoPyJSDynamicAgent(raw=raw)
    elif language == "pexec":
        return AutoExecutionAgent(raw=raw)
    else:
        raise NotImplementedError()  # TODO implement other languages


def get_language_prefix(language):
    if language == "python" or language == "pyjs":
        return "#@"
    elif language == "java":
        return "//@"
    elif language == "c":
        return "//@"
    elif language == "javascript":
        return "//@"
    else:
        raise NotImplementedError()


def clean_code(code, language="python"):
    prefix = get_language_prefix(language)
    return "\n".join(["" if line.strip().startswith(prefix) else line for line in code.split("\n")])


def extract_exec_request(code, language="python"):
    result = []
    prefix = get_language_prefix(language)
    for line in code.split("\n"):
        line = line.strip()
        if line.startswith(prefix):
            exec_request = line[len(prefix):].strip()
            if "(" in exec_request and exec_request.endswith(")"):
                method = exec_request.split("(")[0]
                args_str = exec_request.split("(")[1][:-1]
                # magix regex to split the args
                args = re.split(r',(?![^\[\]\(\)\{\}]*[\]\)\}])', args_str)
                if not "" in map(lambda x: x.strip(), args):
                    result.append((method, list(map(lambda x: x.strip(), args))))
    if len(result) == 0:
        return None
    return result


class Session():
    """A session is a unique identifier for a user. 
    It host the auto agent and the code of the user
    It has a queue of requests to execute and a thread that executes them
    """

    is_launched = False

    def __init__(self, room, socketio, language, raw=False):
        self.room = room
        self.socketio = socketio
        self.language = language
        self.raw = raw
        self.agent = create_agent(language, raw)
        self.code = ""
        self.queue = Queue()
        self.last_execution_line = None
        self.thread = None
        self.launch()
        self.is_launched = True

    def launch(self):
        self.thread = Thread(target=self.event_loop, daemon=True)
        self.thread.start()

    def event_loop(self):
        while True:
            # Wait for a request to execute
            request = self.queue.get()
            # If the request is None, it means the session is closed
            if request is None:
                break
            try:
                self.handle_request(request)
            except Exception as e:
                raise e
            # Notify the queue that the request is done
            self.queue.task_done()

    def handle_request(self, request):
        if request["event"] == "codeChange" or request["event"] == "addSlider":
            session_id = request["session_id"]
            code = clean_code(request["code"], self.language)

            exec_req = extract_exec_request(request["code"], self.language)
            if exec_req is not None:
                changed = self.agent.update_code(code)
                self.send_status("codeChange", session_id=session_id)
                if changed or exec_req != self.last_execution_line or request["event"] == "addSlider":
                    try:
                        result = ""
                        for req in exec_req:
                            result += self.agent.execute(*req)
                            if request["event"] == "addSlider":
                                self.count_iterations(request["lineNumber"], result)
                        self.send({
                            "event": "executeOutput",
                            "output": result,
                        }, json=True)
                        self.last_execution_line = exec_req
                    except TimeoutError:
                        self.send_status("timeout", session_id=session_id)
                        return

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

    def count_iterations(self, line_number, result):
        first_occurrence = None
        last_occurrence = None
        result = json.loads(result)
        for i in range(0, len(result['stacktrace'])):
            if result["stacktrace"][i]["pos"]["line"] == line_number+1:
                if first_occurrence is None:
                    first_occurrence = i
                last_occurrence = i
        self.send({
            "event": "addSlider",
            "lineNumber": line_number,
            "start": first_occurrence,
            "end": last_occurrence,
            "length": last_occurrence - first_occurrence
        }, json=True)

@app.route('/')
def index():
    return render_template('index.html')


# Start the agent with a language parameter
@app.route('/dap/<language>')
def dap(language):
    # create a unique session id
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(session_id, socketio, language, raw=False)
    return render_template('dap.html', language=language, session_id=session_id)


# Start the agent with a language parameter
@app.route('/stack/<language>')
def stack(language):
    # create a unique session id
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(session_id, socketio, language, raw=True)
    return render_template('stackexplorer.html', language=language, session_id=session_id)


@app.route('/stack2/<language>')
def stackt(language):
    # create a unique session id
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(session_id, socketio, language, raw=True)
    return render_template('stackexplorer2.html', language=language, session_id=session_id)


@socketio.on('disconnect')
def on_disconnect():
    if request.sid in sessions_to_sid and (session_id := sessions_to_sid[request.sid]) in sessions:  # type: ignore
        sessions[session_id].agent.agent.stop_server()
        del sessions[session_id]


@socketio.on('join')
def on_join(data):
    session_id = data.get("session_id")
    sessions_to_sid[request.sid] = session_id  # type: ignore
    language = data.get("language")
    join_room(session_id)
    if not session_id in sessions:
        if "stack" in request.referrer:
            sessions[session_id] = Session(session_id, socketio, language, raw=True)
        else:
            sessions[session_id] = Session(session_id, socketio, language, raw=False)
    sessions[session_id].send_status("agent_up", session_id=session_id)


@socketio.on('json')
def handle_json(json_msg):
    session_id = json_msg.get("session_id")
    if session_id is None or session_id not in sessions or (
            session_id in sessions and sessions[session_id].is_launched is False):
        req = {
            "event": "status",
            "status": "launching"
        }
        send(req, json=True)
        return
    sessions[session_id].queue.put(json_msg)


def run():
    # move the current path to this file's path
    import os
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    socketio.run(app)


if __name__ == '__main__':
    run()

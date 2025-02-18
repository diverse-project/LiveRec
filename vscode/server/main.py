import json
from queue import Queue
from threading import Thread
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, join_room, send
from agent import AutoPythonLiveAgent
from dataloader import PythonDataloader
import tempfile
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
sessions = {}

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

sessions_to_sid = {}


class Session():
    """A session is a unique identifier for a user. 
    It host the auto agent and the code of the user
    It has a queue of requests to execute and a thread that executes them
    """
    
    def __init__(self, room, socketio, language, raw=False):
        self.room = room
        self.socketio = socketio
        self.language = language
        self.raw = raw
        self.agent = AutoPythonLiveAgent(raw=raw)
        self.queue = Queue()
        self.last_execution_line = None
        self.thread = None
        self.is_launched = False
        self.launch()
        self.current_execution = None
        self.dataloader = PythonDataloader()

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

    def handle_code_change(self, session_id, code):
        if self.current_execution is not None:
            exec_req = self.current_execution
        else:
            self.send_status("noContext", session_id=session_id)
            return

        changed = self.agent.update_code()
        self.send_status("codeChange", session_id=session_id)
        if changed or exec_req != self.last_execution_line:
            try:
                result = self.agent.execute(*exec_req) # type: ignore
                self.send({
                    "event": "executeOutput",
                    "output": result,
                }, json=True)
                with open(f"execution_history_{id(self)}.stacktraces", "a") as f:
                    f.write(json.dumps({
                        "session_id": self.room,
                        "execution_line": exec_req,
                        "output": result
                    }) + "\n")
                self.last_execution_line = exec_req
            except TimeoutError:
                self.send_status("timeout", session_id=session_id)
                return

        self.send_status("ready", session_id=session_id)

    def handle_select_execution(self, session_id, method : str, args : str):
        self.current_execution = (method, args)
        self.send_status("executionSet", session_id=session_id)
        result = self.agent.execute(*self.current_execution) # type: ignore
        self.send({
            "event": "executeOutput",
            "output": result,
        }, json=True)
        with open(f"execution_history_{id(self)}.stacktraces", "a") as f:
            f.write(json.dumps({
                "session_id": self.room,
                "execution_line": self.current_execution,
                "output": result
            }) + "\n")

    def handle_request(self, request):
        print("[VSCODE SERVER REQUEST processing]", request["event"])
        match request["event"]:
            # Live agent
            case "initialize":
                session_id = request["session_id"]
                if "file_path" in request:
                    self.agent.source_path = request["file_path"]
                    self.agent.agent.set_source_path(request["file_path"])
                self.send_status("agent_up", session_id=session_id)
                self.is_launched = True
            case "codeChange":
                self.handle_code_change(request["session_id"], request["code"])
            case "selectExecution":
                self.handle_select_execution(request["session_id"], request["functionName"], request["args"])
            # Data loading
            case "loadFile":
                try:
                    self.dataloader.load_file(request["file_path"])
                    # Send back loaded functions to update UI immediately
                    functions = self.dataloader.get_functions(request["file_path"])
                    self.send({
                        "event": "functions",
                        "data": functions
                    }, json=True)
                except Exception as e:
                    print(f"Error loading data file: {e}")
                    self.send({
                        "event": "functions",
                        "data": []
                    }, json=True)
                self.send_status("ready", session_id=request["session_id"])
            case "getFunctionData":
                data = self.dataloader.get_function_data(request["file_path"], request["functionName"])
                self.send({
                    "event": "functionData",
                    "data": data
                }, json=True)
            case "getFunctions":
                functions = self.dataloader.get_functions(request["file_path"])
                self.send({
                    "event": "functions",
                    "data": functions
                }, json=True)

    def send(self, data, **kwargs):
        self.socketio.send(data, to=self.room, **kwargs)

    def send_status(self, status, **kwargs):
        req = {
            "event": "status",
            "status": status,
            **kwargs
        }
        self.send(req, json=True)
        

@socketio.on('disconnect')
def on_disconnect():
    if request.sid in sessions_to_sid and (session_id:=sessions_to_sid[request.sid]) in sessions: # type: ignore
        sessions[session_id].agent.agent.stop_server()
        del sessions[session_id]

@socketio.on('join')
def on_join(data):
    session_id = data.get("session_id")
    sessions_to_sid[request.sid] = session_id # type: ignore
    language = data.get("language")
    join_room(session_id)
    if not session_id in sessions:
        if request.referrer is None or "stack" in request.referrer:
            sessions[session_id] = Session(session_id, socketio, language, raw=True)
        else:
            sessions[session_id] = Session(session_id, socketio, language, raw=False)
    sessions[session_id].send_status("agent_up", session_id=session_id)


@socketio.on('json')
def handle_json(json_msg):
    session_id = json_msg.get("session_id")
    if session_id is None or session_id not in sessions:
        print("json message ignored because no session id", json_msg)
        req = {
            "event": "status",
            "status": "launching"
        }
        send(req, json=True) # type: ignore
        return

    session = sessions[session_id]
    event = json_msg.get("event", "")

    # Handle data-related requests even if session is not fully launched
    if event in ["loadFile", "getFunctions", "getFunctionData", "initialize"]:
        session.queue.put(json_msg)
        return
    # For other requests, ensure session is fully launched
    if not session.is_launched:
        print("Message not treated because session is not launched, event:", event)
        req = {
            "event": "status",
            "status": "launching"
        }
        send(req, json=True) # type: ignore
        return

    session.queue.put(json_msg)
    

if __name__ == '__main__':
    socketio.run(app)
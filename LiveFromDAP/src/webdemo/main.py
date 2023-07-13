import time
import uuid
from flask import Flask, render_template
from flask_socketio import SocketIO, send
from webdemo.AutoAgent import AutoCLiveAgent, AutoJavaLiveAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
agent_sessions = {}
last_execution_line = {}

def create_agent(language):
    if language == "c":
        return AutoCLiveAgent()
    elif language == "java":
        return AutoJavaLiveAgent()
    else:
        raise NotImplementedError() # TODO implement other languages
    
def wait_agent_not_buzy(agent):
    while agent.buzy:
        time.sleep(0.1)
        continue

# Start the agent with a language parameter
@app.route('/dap/<language>')
def dap(language):
    # create a unique session id
    session_id = str(uuid.uuid4())
    agent_sessions[session_id] = create_agent(language)
    last_execution_line[session_id] = None
    return render_template('dap.html', language=language, session_id=session_id)

@socketio.on('json')
def handle_json(json_msg):
    if json_msg["event"] == "codeChange":
        session_id = json_msg["session_id"]
        if session_id not in agent_sessions:
            agent_sessions[session_id] = create_agent(json_msg["language"])
            last_execution_line[session_id] = None
        code = clean_code(json_msg["code"])
        wait_agent_not_buzy(agent_sessions[session_id])
        changed = agent_sessions[session_id].update_code(code)
        send_status("codeChange", session_id=session_id)
        exec_req = extract_exec_request(json_msg["code"])
        if exec_req is not None:
            if changed or exec_req != last_execution_line[session_id]:
                result = agent_sessions[session_id].execute(*exec_req)
                send({
                    "event": "executeOutput",
                    "output": result,
                }, json=True)
                last_execution_line[session_id] = exec_req
        send_status("ready", session_id=session_id)
    elif json_msg["event"] == "initialize":
        session_id = json_msg["session_id"]
        if session_id not in agent_sessions:
            agent_sessions[session_id] = create_agent(json_msg["language"])
            last_execution_line[session_id] = None
        send_status("agent_up", session_id=session_id)
        

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


def send_status(status, **kwargs):
    req = {
        "event": "status",
        "status": status,
        **kwargs
    }
    send(req, json=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
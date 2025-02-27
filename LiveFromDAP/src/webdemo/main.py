import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room
from webdemo.config import Config
from webdemo.services.session_manager import SessionManager


app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
socketio = SocketIO(app)
session_manager = SessionManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dap/<language>')
def dap(language):
    print("Creating session")
    session_id = session_manager.create_session(socketio, language, raw=False)
    print("Session created")
    return render_template('dap.html', language=language, session_id=session_id)

@app.route('/stack/<language>')
def stack(language):
    session_id = session_manager.create_session(socketio, language, raw=True)
    return render_template('stackexplorer.html', language=language, session_id=session_id)

@app.route('/vscode/<language>')
def vscode(language):
    session_id = session_manager.create_session(socketio, language, raw=False)
    return render_template('vscode.html', language=language, session_id=session_id)

@socketio.on('disconnect')
def on_disconnect():
    if hasattr(request, "sid"):
        session_id = session_manager.get_session_by_socket(request.sid) # type: ignore
        if session_id:
            session_manager.remove_session(session_id)

@socketio.on('join')
def on_join(data):
    session_id = data.get("session_id")
    language = data.get("language")
    socket_id = request.sid # type: ignore
    
    if not session_id or not socket_id:
        return
        
    session_manager.map_socket_to_session(socket_id, session_id)
    join_room(session_id)
    
    if not session_manager.session_exists(session_id):
        raw = "stack" in request.referrer
        session_manager.create_session(socketio, language, raw=raw)
        
    session = session_manager.get_session(session_id)
    if session:
        session.send_status("agent_up", session_id=session_id)

@socketio.on('json')
def handle_json(json_msg):
    session_id = json_msg.get("session_id")
    if not session_id:
        return
        
    session = session_manager.get_session(session_id)
    if not session or not session.is_launched:
        socketio.send({
            "event": "status",
            "status": "launching"
        }, json=True)
        return
        
    session.queue.put(json_msg)

def run():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    socketio.run(app)

if __name__ == '__main__':
    run()

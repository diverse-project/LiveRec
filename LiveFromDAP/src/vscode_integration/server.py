from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import uuid
from webdemo.AutoAgent import AutoPythonLiveAgent

app = Flask(__name__)
CORS(app)

class FileSession:
    def __init__(self, file_path):
        self.call_count = 0
        self.agent = AutoJavaLiveAgent(raw=False)
        with open(file_path, 'r') as f:
            initial_content = f.read()
        self.agent.update_code(initial_content)
        
    def process(self, content):
        self.call_count += 1
        # Update the agent with new code
        self.agent.update_code(content)
        
        # Keep the current return format
        return {
            'feedback': f"Called {self.call_count} times",
            'hints': [
                {
                    'line': 5,
                    'message': "This is a test"
                }
            ]
        }

# Store active sessions
sessions = {}

@app.route('/init', methods=['POST'])
def init():
    data = request.json
    if not data or 'file_path' not in data:
        return jsonify({'error': 'Missing file_path'}), 400
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = FileSession(data['file_path'])
    return jsonify({'session_id': session_id})

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    if not data or 'session_id' not in data or 'content' not in data:
        return jsonify({'error': 'Missing session_id or content'}), 400
    
    session_id = data['session_id']
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session_id'}), 404
    
    result = sessions[session_id].process(data['content'])
    return jsonify(result)

@app.route('/close', methods=['POST'])
def close():
    data = request.json
    if not data or 'session_id' not in data:
        return jsonify({'error': 'Missing session_id'}), 400
    
    session_id = data['session_id']
    if session_id in sessions:
        # Clean up the agent
        sessions[session_id].agent.agent.stop_server()
        del sessions[session_id]
    return jsonify({'status': 'closed'})

def run_server(port=5000):
    print(f"Server is starting on port {port}...")
    app.run(port=port)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
    run_server(port) 
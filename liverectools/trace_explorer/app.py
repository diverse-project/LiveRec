from flask import Flask, jsonify, render_template, request, send_from_directory
import jsonlines
import json
import os
from pathlib import Path

app = Flask(__name__)

# Get the absolute path to the workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.absolute()
print(WORKSPACE_ROOT)
def load_traces(file_path):
    traces = []
    try:
        # Convert relative path to absolute path
        abs_path = WORKSPACE_ROOT / file_path
        print(f"Loading traces from: {abs_path}")
        
        with jsonlines.open(abs_path) as reader:
            for obj in reader:
                if 'output' in obj:
                    try:
                        # Parse the JSON string in output field
                        parsed_output = json.loads(obj['output'])
                        traces.append({
                            'session_id': obj['session_id'],
                            'execution_line': obj['execution_line'],
                            'stacktrace': parsed_output['stacktrace']
                        })
                    except Exception as e:
                        print(f"Error processing trace: {e}")
    except Exception as e:
        print(f"Error opening file {abs_path}: {e}")
    return traces

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list_trace_files')
def list_trace_files():
    # List all .jsonl files in the workspace and its subdirectories
    trace_files = []
    for path in WORKSPACE_ROOT.rglob('*.stacktraces'):
        if path.is_file():
            # Convert to relative path from workspace root
            rel_path = path.relative_to(WORKSPACE_ROOT)
            trace_files.append(str(rel_path))
    return jsonify(trace_files)

@app.route('/api/traces')
def get_traces():
    # Get the file path from query parameters, default to None
    file_path = request.args.get('file')
    if not file_path:
        return jsonify([])
    
    traces = load_traces(file_path)
    return jsonify(traces)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
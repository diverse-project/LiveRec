from flask import Flask, jsonify, render_template, request, send_from_directory
import jsonlines
import json
import os
from pathlib import Path

app = Flask(__name__)

# Get the absolute path to the workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.absolute()
print(WORKSPACE_ROOT)

def extract_array_from_frame(frame):
    """Extract array data from a stack frame if present."""
    try:
        variables = frame.get('variables', [])
        for var in variables:
            # Look for list/array-like variables
            if var.get('name') == 'arr':  # Specifically look for 'arr' variable
                value = var.get('value')
                if isinstance(value, str) and ('[' in value and ']' in value):
                    try:
                        # Try to parse array-like strings into actual lists
                        array = json.loads(value.replace('(', '[').replace(')', ']'))
                        if isinstance(array, list) and all(isinstance(x, (int, float)) for x in array):
                            return array
                    except:
                        # If the value looks like a Python list literal, try eval
                        if value.strip().startswith('[') and value.strip().endswith(']'):
                            try:
                                array = eval(value)
                                if isinstance(array, list) and all(isinstance(x, (int, float)) for x in array):
                                    return array
                            except:
                                pass
    except Exception as e:
        print(f"Error extracting array: {e}")
    return None

def extract_indices_from_frame(frame):
    """Extract current indices being compared from the frame."""
    try:
        variables = frame.get('variables', [])
        i = j = None
        for var in variables:
            if var.get('name') == 'i':
                i = int(var.get('value'))
            elif var.get('name') == 'j':
                j = int(var.get('value'))
        return i, j
    except:
        return None, None

def extract_source_file(obj):
    """Extract the source file path from the trace data."""
    try:
        execution_line = obj.get('execution_line', [])
        if isinstance(execution_line, list) and len(execution_line) > 0:
            # The first element should be the function name
            return f"code_example/{execution_line[0]}/main.py"
    except:
        pass
    return None

def extract_initial_array(obj):
    """Extract the initial array from the execution line."""
    try:
        execution_line = obj.get('execution_line', [])
        if isinstance(execution_line, list) and len(execution_line) > 1:
            params = execution_line[1]
            if isinstance(params, dict) and 'arr' in params:
                return params['arr']
    except:
        pass
    return None

def load_traces(file_path):
    executions = {}  # Dictionary to store traces grouped by execution
    try:
        # Convert relative path to absolute path
        abs_path = WORKSPACE_ROOT / file_path
        print(f"Loading traces from: {abs_path}")
        
        with jsonlines.open(abs_path) as reader:
            current_session = None
            current_traces = []
            source_file = None
            execution_count = 0
            
            for obj in reader:
                if source_file is None:
                    source_file = extract_source_file(obj)
                
                # Get the initial array for this execution
                initial_array = extract_initial_array(obj)
                if initial_array:
                    session_id = obj['session_id']
                    execution_count += 1
                    execution_key = f"{session_id}_{execution_count}"
                    
                    # If we find a new execution, store the previous one
                    if current_session and current_traces:
                        executions[current_session] = {
                            'traces': current_traces,
                            'initial_array': initial_array,
                            'source_file': source_file
                        }
                        current_traces = []
                    
                    current_session = execution_key
                
                if 'output' in obj:
                    try:
                        # Parse the JSON string in output field
                        parsed_output = json.loads(obj['output'])
                        stacktrace = parsed_output.get('stacktrace', [])
                        
                        # Process each frame in the stacktrace
                        for frame in stacktrace:
                            array_data = extract_array_from_frame(frame)
                            if array_data is not None:
                                i, j = extract_indices_from_frame(frame)
                                current_traces.append({
                                    'session_id': obj['session_id'],
                                    'execution_line': frame['pos']['line'],
                                    'array_data': array_data,
                                    'compare_indices': {'i': i, 'j': j},
                                    'source_file': source_file
                                })
                    except Exception as e:
                        print(f"Error processing trace: {e}")
            
            # Store the last execution
            if current_session and current_traces:
                executions[current_session] = {
                    'traces': current_traces,
                    'initial_array': initial_array,
                    'source_file': source_file
                }
    
    except Exception as e:
        print(f"Error opening file {abs_path}: {e}")
    
    return executions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list_trace_files')
def list_trace_files():
    # List all .stacktraces files in the workspace and its subdirectories
    trace_files = []
    for path in WORKSPACE_ROOT.rglob('*.stacktraces'):
        if path.is_file():
            # Convert to relative path from workspace root
            rel_path = path.relative_to(WORKSPACE_ROOT)
            trace_files.append(str(rel_path))
    return jsonify(trace_files)

@app.route('/api/executions')
def get_executions():
    """Get list of available executions in a trace file."""
    file_path = request.args.get('file')
    if not file_path:
        return jsonify([])
    
    executions = load_traces(file_path)
    return jsonify([{
        'id': execution_id,
        'initial_array': data['initial_array']
    } for execution_id, data in executions.items()])

@app.route('/api/traces')
def get_traces():
    """Get traces for a specific execution."""
    file_path = request.args.get('file')
    execution_id = request.args.get('execution')
    if not file_path or not execution_id:
        return jsonify([])
    
    executions = load_traces(file_path)
    if execution_id in executions:
        return jsonify(executions[execution_id])
    return jsonify([])

@app.route('/api/code')
def get_code():
    """Serve the source code file."""
    file_path = request.args.get('file')
    if not file_path:
        return "No file specified", 400
    
    try:
        abs_path = WORKSPACE_ROOT / file_path
        if not abs_path.is_file():
            return "File not found", 404
        
        with open(abs_path, 'r') as f:
            return f.read()
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
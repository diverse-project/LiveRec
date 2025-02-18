# Execution Trace Explorer

A web-based tool for exploring execution traces from JSONL files. This tool provides an interactive interface to view and analyze execution stacktraces, variables, and their values at different points in the code execution.

## Features

- View execution traces in a clean, organized interface
- Browse through different execution sessions
- Examine stackframes with detailed variable information
- See code location (line and column) for each stack frame
- Interactive UI with Bootstrap styling

## Setup

1. Create a Python virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. The left panel shows a list of all execution traces
2. Click on any trace to view its details in the right panel
3. For each trace, you can see:
   - Session ID
   - Function name
   - Complete stacktrace with:
     - Code location (line and column)
     - Variables and their values
     - Variable types

## Data Format

The tool expects execution traces in JSONL format with the following structure:
```json
{
    "session_id": "unique-session-id",
    "execution_line": ["function_name", {...}],
    "output": "{\"stacktrace\": [...]}"
}
``` 
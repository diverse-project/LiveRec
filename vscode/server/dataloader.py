import json
from typing import Dict, List, Any, cast
from datetime import datetime
import jsonpickle

class PythonDataloader:
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
        self.executions_by_function: Dict[str, List[Dict[str, Any]]] = {}

    def load_data(self, data: list):
        self.data.extend(data)
        self._process_data()

    def load_file(self, file_path: str):
        self.data = []  # Clear existing data
        with open(file_path, "r") as f:
            for line in f:
                # Use jsonpickle to decode the entire line to preserve object structure
                decoded = jsonpickle.decode(line)
                self.data.append(cast(Dict[str, Any], decoded))
        self._process_data()

    def _process_data(self):
        """Process the raw data into a more usable format, grouping executions by function."""
        self.executions_by_function = {}
        current_executions: Dict[str, Dict[str, Any]] = {}

        for event in self.data:
            if event['event_type'] == 'call':
                # Start of a function execution
                execution_id = event['execution_id']
                function_name = event['function']
                current_executions[execution_id] = {
                    'function': function_name,
                    'line': event['line'],
                    'locals': event['locals'],
                    'globals': event['globals'],
                    'timestamp': event['timestamp'],
                    'parent_id': event['parent_id'],
                    'file': event['file']
                }
            elif event['event_type'] == 'return':
                # End of a function execution
                execution_id = event['execution_id']
                if execution_id in current_executions:
                    execution = current_executions[execution_id]
                    # Decode the return value using jsonpickle
                    execution['return'] = jsonpickle.decode(event['return_value'])
                    execution['end_timestamp'] = event['timestamp']
                    
                    # Calculate execution time
                    start_time = datetime.fromisoformat(execution['timestamp'])
                    end_time = datetime.fromisoformat(event['timestamp'])
                    execution['exec_time'] = (end_time - start_time).total_seconds()

                    # Add to executions by function
                    function_name = execution['function']
                    if function_name not in self.executions_by_function:
                        self.executions_by_function[function_name] = []
                    self.executions_by_function[function_name].append(execution)
                    
                    # Remove from current executions
                    del current_executions[execution_id]

    def get_function_data(self, file_path: str, function_name: str) -> List[Dict[str, Any]]:
        """Get all executions of a specific function."""
        if function_name not in self.executions_by_function:
            return []

        executions = self.executions_by_function[function_name]
        return [
            {
                'locals': exec['locals'],
                'globals': exec['globals'],
                'return': exec['return'],
                'timestamp': exec['timestamp'],
                'exec_time': exec['exec_time'],
                'args': self._extract_args(exec['locals'])
            }
            for exec in executions
            if exec['file'] == file_path
        ]

    def _extract_args(self, locals_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Extract function arguments from locals dictionary."""
        args = {k: v for k, v in locals_dict.items()}
        return args

    def get_functions(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all functions that have been executed in the specified file."""
        functions = set()
        for executions in self.executions_by_function.values():
            for exec in executions:
                if exec['file'] == file_path:
                    functions.add((exec['function'], exec['line']))

        return [
            {
                'name': function_name,
                'line': line
            }
            for function_name, line in sorted(functions, key=lambda x: x[1])
        ]

    def get_inside_function(self, file_path: str, function_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all executions that happened inside a specific function execution."""
        result = {}
        for executions in self.executions_by_function.values():
            for exec in executions:
                if exec['file'] == file_path and exec['function'] == function_name:
                    result[function_name] = self.get_function_data(file_path, function_name)
        return result

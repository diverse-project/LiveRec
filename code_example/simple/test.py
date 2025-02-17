import time
from livefromdap.agent.PythonLiveAgent2 import PythonLiveAgent
import os
import json
agent = PythonLiveAgent(debug=False)
agent.start_server()
agent.initialize()

def execute_test(exec : str):
    output = agent.execute("Test.normal_function", json.loads(exec))
    return_value, stacktrace = output
    stacktrace.last_stackframe.variables.append({"name":"return", "value":return_value})
    st = json.dumps({
        "return_value": return_value,
        "stacktrace": stacktrace.to_json()
    })
    with open("simple_test.stacktraces", "a") as f:
        f.write(json.dumps({
                            "session_id": "test",
                            "execution_line": exec,
                            "output": st
                        }) + "\n")


agent.set_source_path(os.path.join(os.path.dirname(__file__), "main.py"))
execution = '{"self": {"py/object": "__main__.Test", "inside": 10}, "x": 2}'


# rm the stacktraces file if it exists
if os.path.exists("simple_test.stacktraces"):
    os.remove("simple_test.stacktraces")



for i in [2,3]:
    agent.mock_function("long_function", '[{"py/tuple": [{"self": {"py/object": "__main__.Test", "inside": 10}, "x": 2},'+str(i)+']}]')
    execute_test(execution)


agent.stop_server()



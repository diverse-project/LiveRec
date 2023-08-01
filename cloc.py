import os
import json

BASE_COMMAND = "cloc --vcs git --json"

report = {
    "Java JDI":{},
    "DAP Base":{},
    "DAP Python":{},
    "DAP Java":{},
    "DAP JavaScript":{},
    "DAP C":{},
}

def extract(root_path, files):
    command = BASE_COMMAND + " " + " ".join([os.path.join(root_path, f) for f in files])
    result = os.popen(command).read()
    return json.loads(result)

# Java JDI server
root_path = "JavaProbes/src/main/java/debugger/"
files = ["Debugger.java", "MirrorCreator.java", "ObjectInvocationRequest.java", "StackFrame.java", "StackRecording.java"]
report["Java JDI"]["Server"] = extract(root_path, files)["Java"]["code"]
# Java JDI KAA
files = ["DebugAgent.java", "DynamicClassLoader.java", "DynamicClassLoaderFactory.java"]
report["Java JDI"]["KAA"] = extract(root_path, files)["Java"]["code"]

# DAP Base
root_path = "LiveFromDAP/src/livefromdap/"
files = ["agent/BaseLiveAgent.py", "utils/StackRecording.py"]
report["DAP Base"]["Server"] = extract(root_path, files)["Python"]["code"]
report["DAP Base"]["KAA"] = 0

# DAP Python
report["DAP Python"]["Server"] = extract(root_path, ["agent/PythonLiveAgent.py"])["Python"]["code"]
report["DAP Python"]["KAA"] = extract(root_path, ["runner/py_runner.py"])["Python"]["code"]

# DAP Java
report["DAP Java"]["Server"] = extract(root_path, ["agent/JavaLiveAgent.py"])["Python"]["code"]
files = ["runner/Runner.java", "runner/DynamicClassLoader.java", "runner/DynamicClassLoaderFactory.java"]
report["DAP Java"]["KAA"] = extract(root_path, files)["Java"]["code"]

# DAP JavaScript
report["DAP JavaScript"]["Server"] = extract(root_path, ["agent/JavascriptLiveAgent.py"])["Python"]["code"]
report["DAP JavaScript"]["KAA"] = extract(root_path, ["runner/js_runner.js"])["JavaScript"]["code"]

# DAP C
report["DAP C"]["Server"] = extract(root_path, ["agent/CLiveAgent.py"])["Python"]["code"]
report["DAP C"]["KAA"] = extract(root_path, ["runner/c_runner.c"])["C"]["code"]

print(json.dumps(report, indent=4))



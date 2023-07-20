import os
import json
import re
import subprocess
import time
from Scenario import Scenario
from livefromdap import JavaLiveAgent




if not os.path.exists("tmp"):
    os.makedirs("tmp")

class_name = "BinarySearch"
method = "binarySearch"
source_path = os.path.abspath("tmp/BinarySearch.java")
class_path = os.path.abspath("tmp/")    
scenario = Scenario(os.path.abspath("binary_search"), "java", ".java", source_path)
times = {
    "init": 0,
    "scenario":{}
}

def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    return process.returncode

def compile_java():
    execute_command(f"javac -g -d {class_path} {source_path}")

# Python
print(" == Starting == ")
t1 = time.time()
agent = JavaLiveAgent(debug=False)
agent.start_server()
agent.initialize()
t2 = time.time()
times["init"] = t2-t1

for i, (args_str, ret, comp) in enumerate(scenario):
    print("Iteration: ", i, end="\r")
    times['scenario'][i] = {}
    args = re.split(r',(?![^\[\]\(\)\{\}]*[\]\)\}])', args_str)
    args = list(map(lambda x: x.strip(), args))
    t1 = time.time()
    if comp == "true":
        compile_java()
        agent.load_code(class_path, class_name)
    res, st = agent.execute(class_name, method, args, max_steps=80)
    t2 = time.time()
    times['scenario'][i]['exec'] = t2-t1
    times['scenario'][i]['step'] = len(st)
    assert res == ret, f"Expected {ret}, got {res}"
    
agent.stop_server()
print("")
with open("binary_search_java_times.json", 'w') as file:
    json.dump(times, file, indent=4)
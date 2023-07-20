import os
import json
import re
import subprocess
import time
from Scenario import Scenario
from livefromdap import CLiveAgent

if not os.path.exists("tmp"):
    os.makedirs("tmp")


method = "binary_search"
source_path = os.path.abspath("tmp/binary_search.c")
compiled_path = os.path.abspath("tmp/binary_search.so")
scenario = Scenario(os.path.abspath("binary_search"), "c", ".c", source_path)
times = {
    "init": 0,
    "scenario":{}
}

def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    return process.returncode

def compile_c():
    execute_command(f"gcc -g -fPIC -shared -o {compiled_path} {source_path}")


print(" == Starting == ")
t1 = time.time()
agent = CLiveAgent(debug=False)
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
        compile_c()
        agent.load_code(compiled_path)
    res, st = agent.execute(source_path, method, args, max_steps=80)
    t2 = time.time()
    times['scenario'][i]['exec'] = t2-t1
    times['scenario'][i]['step'] = len(st)
    assert str(res).strip() == str(ret).strip(), f"Expected '{ret}', got '{res}'"
    
agent.stop_server()
print("")
with open("binary_search_c_times.json", 'w') as file:
    json.dump(times, file, indent=4)
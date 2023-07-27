import os
import json
import re
import time
from Scenario import Scenario
from livefromdap import JavascriptLiveAgent


if not os.path.exists("tmp"):
    os.makedirs("tmp")

method = "binary_search"
source_path = os.path.abspath("tmp/binary_search.js")
scenario = Scenario(os.path.abspath("binary_search"), "javascript", ".js", os.path.abspath("tmp/binary_search.js"))
times = {
    "init": 0,
    "scenario":{}
}

# Python
print(" == Starting == ")
t1 = time.time()
agent = JavascriptLiveAgent(debug=False)
agent.start_server()
agent.initialize()
t2 = time.time()
times["init"] = t2-t1

for i, (args_str, ret, _) in enumerate(scenario):
    print("Iteration: ", i, end="\r")
    times['scenario'][i] = {}
    args = re.split(r',(?![^\[\]\(\)\{\}]*[\]\)\}])', args_str)
    args = list(map(lambda x: x.strip(), args))
    t1 = time.time()
    agent.load_code(source_path)
    t2 = time.time()
    times['scenario'][i]['load'] = t2-t1
    
    t1 = time.time()
    res, st = agent.execute(source_path, method, args,max_steps=80)
    t2 = time.time()
    times['scenario'][i]['exec'] = t2-t1
    times['scenario'][i]['step'] = len(st)
    assert res == ret
    
agent.stop_server()
print("")
with open("binary_search_javascript_times.json", 'w') as file:
    json.dump(times, file, indent=4)
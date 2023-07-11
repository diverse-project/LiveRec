import os
import subprocess

import pandas as pd
from livefromdap.agent.JavaLiveAgentPerf import JavaLiveAgentPerf
import time
from matplotlib import pyplot as plt

agent = JavaLiveAgentPerf(
    debug=False) # Turn this to True to see the debug messages

agent.start_server()
agent.initialize()

def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    return process.returncode

code_template = """
public class UselessClass {{
    public static int uselessMethod(int step) {{
        int res = {};
        for (int i = 0; i < step; i++) {{
            res += i;
        }}
        return res;
    }}   
}}
"""

res = []

for i in range(1, 200):
    print("Iteration: ", i)
    with open(os.path.join("tmp", "UselessClass.java"), "w") as f:
        f.write(code_template.format(i))
    t1 = time.time()
    execute_command("javac -g -d tmp tmp/UselessClass.java")
    t2 = time.time()
    agent.load_code(os.path.abspath("tmp"), "UselessClass")
    t3 = time.time()
    _,_,times = agent.execute("UselessClass", "uselessMethod", [str(i)])
    t4 = time.time()
    times["step"] = i
    times["compile"] = t2 - t1
    times["load_code"] = t3 - t2
    times["execute"] = t4 - t3
    res.append(times)

df = pd.DataFrame(res)
df.to_csv("java_perf.csv")

agent.stop_server()

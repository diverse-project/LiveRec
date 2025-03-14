import os
import subprocess
import time
from livefromdap import CLiveAgent,PythonLiveAgent,JavaLiveAgent
from livefromdap.agent.JavascriptLiveAgent import JavascriptLiveAgent

def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    return process.returncode


# if tmp folder does not exist, create it
if not os.path.exists("tmp"):
    os.makedirs("tmp")

# C
c_code_template = """
int useless_method(int x) {{
    int d = 0;
    for (int i = 0; i < x; i++) {{
        d += i;
    }}
    return d;
}}
"""
def compile_c():
    execute_command("gcc -g -fPIC -shared -o tmp/useless.so tmp/useless.c")

with open(os.path.join("tmp", "useless.c"), "w") as f:
    f.write(c_code_template.format())
compile_c()

c_source_path = os.path.abspath("tmp/useless.c")
c_compiled_path = os.path.abspath("tmp/useless.so")
c_method = "useless_method"


# Python
python_code_template = """
def useless_method(x):
    d = 0
    for i in range(x):
        d += i
    return d
"""

with open(os.path.join("tmp", "useless.py"), "w") as f:
    f.write(python_code_template.format())

python_source_path = os.path.abspath("tmp/useless.py")
python_method = "useless_method"

# Java
java_code_template = """
public class ExecutePerformance {{
    public static int executePerformanceMethod(int x) {{
        int d = 0;
        for (int i = 0; i < x; i++) {{
            d += i;
        }}
        return d;
    }}   
}}
"""
def compile_java():
    execute_command("javac -g -d tmp tmp/ExecutePerformance.java")

with open(os.path.join("tmp", "ExecutePerformance.java"), "w") as f:
    f.write(java_code_template.format())
compile_java()
java_class_path = os.path.abspath("tmp")
java_class_name = "ExecutePerformance"
java_method = "executePerformanceMethod"

# JS

js_code_template = """
function useless_method(x) {{
    let d = 0;
    for (let index = 0; index < x; index++) {{
        d += index;
    }}
    return d;
}}
"""

with open(os.path.join("tmp", "useless.js"), "w") as f:
    f.write(js_code_template.format())

js_source_path = os.path.abspath("tmp/useless.js")
js_method = "useless_method"

times = {
    "c": {},
    "python": {},
    "java": {},
    "js": {}
}

# C
print(" == C == ")
agent = CLiveAgent(debug=False)
agent.start_server()
agent.initialize()
agent.load_code(c_compiled_path)

# warm up
for _ in range(5):
    agent.execute(c_source_path, c_method, ["3"], max_steps=1000000)

for i in range(50):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    _, st = agent.execute(c_source_path, c_method, [str(i+1)], max_steps=1000000)
    t2 = time.time()
    times["c"][len(st.stackframes)] = t2 - t1
agent.stop_server()
print("")

# Python
print(" == Python == ")
agent = PythonLiveAgent(debug=False)
agent.start_server()
agent.initialize()
agent.load_code(python_source_path)

# warm up
for _ in range(5):
    agent.execute(python_method, ["3"], max_steps=1000000)
    
for i in range(50):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    _, st = agent.execute(python_method, [str(i+1)], max_steps=1000000)
    t2 = time.time()
    times["python"][len(st.stackframes)] = t2 - t1
agent.stop_server()
print("")


# Java

print(" == Java == ")
agent = JavaLiveAgent(debug=False)
agent.start_server()
agent.initialize()
agent.load_code(java_class_path, java_class_name)

#warm up
for _ in range(5):
    agent.execute(java_class_name, java_method, ["3"], max_steps=1000000)
    
for i in range(50):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    _, st = agent.execute(java_class_name, java_method, [str(i+1)], max_steps=1000000)
    t2 = time.time()
    times["java"][len(st.stackframes)] = t2 - t1

agent.stop_server()
print("")


# JS
print(" == Javascript == ")
agent = JavascriptLiveAgent(debug=False)
agent.start_server()
agent.initialize()
agent.load_code(js_source_path)

# warm up
for _ in range(3):
    agent.execute(js_source_path, js_method, ["1"], max_steps=1000000)
    
for i in range(33):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    _, st = agent.execute(js_source_path, js_method, [str(i+1)], max_steps=1000000)
    t2 = time.time()
    times["js"][len(st.stackframes)] = t2 - t1

agent.stop_server()
print("")

# convert to dataframe
import pandas as pd
df = pd.DataFrame(times)
df.to_csv("execute_performance.csv")
print(df)


import os
import subprocess
import time
from livefromdap import CLiveAgent,PythonLiveAgent,JavaLiveAgent

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
    int l = x;{}
    return x;
}}
"""
def compile_c():
    execute_command("gcc -g -fPIC -shared -o tmp/useless.so tmp/useless.c")
def update_c_file(line):
    with open(os.path.join("tmp", "useless.c"), "w") as f:
        f.write(c_code_template.format("\nl++;"*line))
    compile_c()

update_c_file(0)
c_source_path = os.path.abspath("tmp/useless.c")
c_compiled_path = os.path.abspath("tmp/useless.so")
c_method = "useless_method"


# Python
python_code_template = """
def useless_method(x):
    res = x{}
    return res
"""
def update_python_file(line):
    with open(os.path.join("tmp", "useless.py"), "w") as f:
        f.write(python_code_template.format("\n    res += 1"*line))

update_python_file(0)
python_source_path = os.path.abspath("tmp/useless.py")
python_method = "useless_method"

# Java
java_code_template = """
public class UselessClass {{
    public static int uselessMethod(int x) {{
        int a = x;{}
        return a;
    }}   
}}
"""
def compile_java():
    execute_command("javac -g -d tmp tmp/UselessClass.java")

def update_java_file(line):
    with open(os.path.join("tmp", "UselessClass.java"), "w") as f:
        f.write(java_code_template.format("\na++; "*line))
    compile_java()

update_java_file(0)
java_class_path = os.path.abspath("tmp")
java_class_name = "UselessClass"
java_method = "uselessMethod"



times = {
    "c": [],
    "python": [],
    "java": []
}

# C
print(" == C == ")
agent = CLiveAgent(debug=False)
agent.start_server()
agent.initialize()
for i in range(100):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    agent.load_code(c_compiled_path)
    t2 = time.time()
    update_c_file(i+1)
    times["c"].append(t2 - t1)
agent.stop_server()
print("")

# Python
print(" == Python == ")
agent = PythonLiveAgent(debug=False)
agent.start_server()
agent.initialize()
for i in range(100):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    agent.load_code(python_source_path)
    t2 = time.time()
    update_python_file(i+1)
    times["python"].append(t2 - t1)
    
agent.stop_server()
print("")


# Java

print(" == Java == ")
agent = JavaLiveAgent(debug=False)
agent.start_server()
agent.initialize()
for i in range(100):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    agent.load_code(java_class_path, java_class_name)
    t2 = time.time()
    update_java_file(i+1)
    times["java"].append(t2 - t1)
agent.stop_server()
print("")

# convert to dataframe
import pandas as pd
df = pd.DataFrame(times)
df.to_csv("performance/load_code_performance.csv")
print(df)


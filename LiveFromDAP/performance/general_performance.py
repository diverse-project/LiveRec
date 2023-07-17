import os
import subprocess
import time
from livefromdap import CLiveAgent,PythonLiveAgent,JavaLiveAgent

def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    return process.returncode

def compile_c():
    execute_command("gcc -g -fPIC -shared -o src/livefromdap/target/c/binary_search.so src/livefromdap/target/c/binary_search.c")

def compile_java():
    execute_command("javac -g -d src/livefromdap/target/java src/livefromdap/target/java/BinarySearch.java")

# C
c_source_path = os.path.abspath("src/livefromdap/target/c/binary_search.c")
c_compiled_path = os.path.abspath("src/livefromdap/target/c/binary_search.so")
c_method = "binary_search"
c_args = ["{1,2,3,4,5,6}", "6", "9"]

# Python
python_source_path = os.path.abspath("src/livefromdap/target/python/binary_search.py")
python_method = "binary_search"
python_args = ["[1,2,3,4,5,6]", "9"]

# Java
java_class_path = os.path.abspath("src/livefromdap/target/java")
java_class_name = "BinarySearch"
java_method = "binarySearch"
java_args = ["new char[]{'a', 'b','c','d','e','f'}", "'i'"]

times = {
    "c": {
        "initialize": 0,
        "compile": 0,
        "load_code": 0,
        "execute": 0
    },
    "python": {
        "initialize": 0,
        "compile": 0,
        "load_code": 0,
        "execute": 0
    },
    "java": {
        "initialize": 0,
        "compile": 0,
        "load_code": 0,
        "execute": 0
    }
}

# C
print(" == C == ")
t1 = time.time()
agent = CLiveAgent(debug=False)
agent.start_server()
agent.initialize()
t2 = time.time()
times["c"]["initialize"] = t2 - t1
for i in range(100):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    compile_c()
    t2 = time.time()
    times["c"]["compile"] += t2 - t1
    t1 = time.time()
    agent.load_code(c_compiled_path)
    t2 = time.time()
    times["c"]["load_code"] += t2 - t1
    t1 = time.time()
    agent.execute(c_source_path, c_method, c_args)
    t2 = time.time()
    times["c"]["execute"] += t2 - t1
agent.stop_server()
print("")
times["c"]["compile"] /= 100
times["c"]["load_code"] /= 100
times["c"]["execute"] /= 100

# Python
print(" == Python == ")
t1 = time.time()
agent = PythonLiveAgent(debug=False)
agent.start_server()
agent.initialize()
t2 = time.time()
times["python"]["initialize"] = t2 - t1
for i in range(100):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    agent.load_code(python_source_path)
    t2 = time.time()
    times["python"]["load_code"] += t2 - t1
    t1 = time.time()
    agent.execute(python_method, python_args)
    t2 = time.time()
    times["python"]["execute"] += t2 - t1
agent.stop_server()
print("")
times["python"]["load_code"] /= 100
times["python"]["execute"] /= 100

# Java

print(" == Java == ")
t1 = time.time()
agent = JavaLiveAgent(debug=False)
agent.start_server()
agent.initialize()
t2 = time.time()
times["java"]["initialize"] = t2 - t1
for i in range(100):
    print("Iteration: ", i, end="\r")
    t1 = time.time()
    compile_java()
    t2 = time.time()
    times["java"]["compile"] += t2 - t1
    t1 = time.time()
    agent.load_code(java_class_path, java_class_name)
    t2 = time.time()
    times["java"]["load_code"] += t2 - t1
    t1 = time.time()
    agent.execute(java_class_name, java_method, java_args)
    t2 = time.time()
    times["java"]["execute"] += t2 - t1
agent.stop_server()
print("")
times["java"]["compile"] /= 100
times["java"]["load_code"] /= 100
times["java"]["execute"] /= 100


# convert to dataframe
import pandas as pd
df = pd.DataFrame(times)
df.to_csv("performance/general_performance.csv")
print(df)


import os
import subprocess
import time
from livefromdap import CLiveAgent,PythonLiveAgent,JavaLiveAgent

def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    return process.returncode


def compile_java():
    execute_command("javac -g -d src/livefromdap/target/java src/livefromdap/target/java/BinarySearch.java")

# C
c_code_template = """
int binary_search(int arr[], int length, int target) {{
    int left = 0;
    int right = length - 1;
    while (left <= right) {{

        int mid = (left + right) / 2;
        if (arr[mid] == target) {{
            return mid;
        }} else if (arr[mid] < target) {{
            left = mid + 1;
        }} else {{
            right = mid - 1;
        }}
    }}
    return {};
}}
"""
def compile_c():
    execute_command("gcc -g -fPIC -shared -o tmp/binary_search.so tmp/binary_search.c")
def update_c_file(value):
    with open(os.path.join("tmp", "binary_search.c"), "w") as f:
        f.write(c_code_template.format(value))
    compile_c()
update_c_file(-1)
c_source_path = os.path.abspath("tmp/binary_search.c")
c_compiled_path = os.path.abspath("tmp/binary_search.so")
c_method = "binary_search"
c_args = ["{1,2,3,4,5,6}", "6", "9"]

# Python
python_code_template = """
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return {}
"""
def update_python_file(value):
    with open(os.path.join("tmp", "binary_search.py"), "w") as f:
        f.write(python_code_template.format(value))
update_python_file(-1)
python_source_path = os.path.abspath("tmp/binary_search.py")
python_method = "binary_search"
python_args = ["[1,2,3,4,5,6]", "9"]

# Java
java_code_template = """
public class BinarySearch {{
    public static int binarySearch(int[] array, int key) throws InterruptedException {{
        int low = 0;
        int high = array.length - 1;
        while (low <= high) {{
            int mid = (low + high) / 2;
            int value = array[mid];
            if (value < key) {{
                low = mid + 1;
            }} else if (value > key) {{
                high = mid - 1;
            }} else {{
                return mid;
            }}
        }}
        return {};
    }}
}}
"""
def compile_java():
    execute_command("javac -g -d tmp tmp/BinarySearch.java")

def update_java_file(value):
    with open(os.path.join("tmp", "BinarySearch.java"), "w") as f:
        f.write(java_code_template.format(value))
    compile_java()
update_java_file(-1)
java_class_path = os.path.abspath("tmp")
java_class_name = "BinarySearch"
java_method = "binarySearch"
java_args = ["new int[]{1,2,3,4,5,6}", "9"]

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
    update_c_file(i)
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
    update_python_file(i)
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
    update_java_file(i)
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


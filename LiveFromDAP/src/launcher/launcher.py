import subprocess
import sys, os#, argparse
import pandas as pd
from matplotlib import pyplot as plt
import time
sys.path.append(os.path.join(os.path.dirname(sys.path[0])))
import instrumentation as instr
from webdemo.services.code_processor import LivExCodeProcessor
from livefromdap.agent.PyPolyglotLivExAgent import PyPolyglotLivExAgent
from livefromdap.agent.JSPolyglotLivExAgent import JSPolyglotLivExAgent

repeats = 5
folder = "/code/tests/benchmarks/"
polyglot_files = [("fasta/fasta_replace" , ["ex1"]), 
                 ("fasta/genrandom_replace", ["ex1", "ex2"]),
                 ("nbody/advance_replace", ["ex1", "ex2", "ex3", "ex4"]),
                 ("nbody/loop_replace", ["ex1", "ex2", "ex3", "ex4"]),
                 ("pidigits/loop_replace", ["ex1", "ex2", "ex3", "ex4"])]

py_files = [("py_stdlib_tests/test_json",[f"ex{i+1}" for i in range(19)]),
                 ("py_stdlib_tests/test_string",[f"ex{i+1}" for i in range(35)]),
                 ("numpy_tests", [f"ex{i+1}" for i in range(74)])]
file_suffix = "/entry"


js_files = [("moment_tests", [f"ex{i+1}" for i in range(15)]),
            ("nodejs_tests", [f"ex{i+1}" for i in range(4)])]



processor = LivExCodeProcessor()

def run_file(file, examples, agent, language, repeat_amount=10):
    with open(file, "r") as f:
        original_code = f.read()

    for example_name in examples:
        for i in range(repeat_amount):
            print(f"Running example {example_name} in file {file} ({i})")
            

            exec_req = LivExCodeProcessor.extract_exec_request(original_code, language, example_name)
            cleaned_code = LivExCodeProcessor.clean_code(original_code, [exec_req], language)

            method, args, probes = exec_req

            with open(file, "w") as f:
                f.write(cleaned_code)

            
            start = time.time()
            agent.load_code(file) 
            result = agent.execute(method, args, probes)
            end = time.time()

            print(f"Example run time {end-start}")
            # restore file
            with open(file, 'w') as f:
                f.write(original_code)
            
    # For some reason the JS DAP doesn't properly kill itself when asked nicely (conflict between the 2nd and 3rd law most likely), so we have to do it ourselves 
    processlist = subprocess.getstatusoutput("ps ax | grep 'node ./js_runner.js' | grep -v 'grep' | awk '{print $1}'")
    print(processlist[1])
    for pid in processlist[1].split("\n"):
        kill = subprocess.getstatusoutput(f"kill {pid}")
    

total_start = time.time()

for file_info in polyglot_files:
    lang_extension = ".py"
    language = "python"
    agent = PyPolyglotLivExAgent()
    agent.start_server()
    agent.initialize()
    fileName, examples = file_info
    file = folder + fileName + file_suffix + lang_extension
    run_file(file, examples, agent, language, repeats)
    agent.stop_server()

dfp1 = pd.DataFrame(instr.py_local_probe_times, columns=["Simple probes"])
dfp2 = pd.DataFrame(instr.js_foreign_record_times, columns=["Foreign recording steps"])

instr.py_local_probe_times = []

for file_info in py_files:
    lang_extension = ".py"
    language = "python"
    agent = PyPolyglotLivExAgent()
    agent.start_server()
    agent.initialize()
    fileName, examples = file_info
    file = folder + fileName + file_suffix + lang_extension
    run_file(file, examples, agent, language, repeats)
    agent.stop_server()
    

for file_info in js_files:
    lang_extension = ".js"
    language = "javascript"
    agent = JSPolyglotLivExAgent()
    agent.start_server()
    agent.initialize()
    fileName, examples = file_info
    file = folder + fileName + file_suffix + lang_extension
    run_file(file, examples, agent, language, repeats)
    agent.stop_server()


total_end = time.time()
print(f"Total run time: {total_end-total_start}")

dfp3 = dfp1.join([dfp2], how='outer')
dfp3.to_csv("/results/polyglot_times.csv")
dfp3.boxplot()
plt.savefig("/results/polyglot_times.png")
plt.clf()

df1 = pd.DataFrame(instr.py_local_probe_times, columns=["Python probes"])
df2 = pd.DataFrame(instr.js_local_probe_times, columns=["JavaScript probes"])
df3 = df1.join([df2], how='outer')
df3.to_csv("/results/probe_times.csv")
df3.boxplot()
plt.savefig("/results/probe_times.png")
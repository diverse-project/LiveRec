import sys, os, argparse
import time
sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from webdemo.services.code_processor import LivExCodeProcessor
from livefromdap.agent.PolyglotLivExAgent import PolyglotLivExAgent

# TODO: Receive a file + a selected example, execute that example and output results
parser = argparse.ArgumentParser()
parser.add_argument("file", help="The example-containing file to be launched")
args = parser.parse_args()
# /code/tests/benchmarks/fasta/genrandom_replace/entry.py
file = args.file
example_name = "ex1"
language = "python"

with open(file, "r") as f:
    original_code = f.read()

processor = LivExCodeProcessor()

agent = PolyglotLivExAgent()
agent.start_server()
agent.initialize()

exec_req = LivExCodeProcessor.extract_exec_request(original_code, language, example_name)
cleaned_code = LivExCodeProcessor.clean_code(original_code, [exec_req], language)

method, args, probes = exec_req

with open(file, "w") as f:
    f.write(cleaned_code)

start = time.time()
agent.load_code(file) #TODO: append system path before exec to enable imports to work
result = agent.execute(method, args, probes)
end = time.time()

print(f"[DBG] Time {end-start}")

# restore file
with open(file, 'w') as f:
    f.write(original_code)
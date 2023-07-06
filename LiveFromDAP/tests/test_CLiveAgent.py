from livefromdap.agent.CLiveAgent import CLiveAgent
import os
import time

# Compile command : gcc -g -fPIC -shared -o target/binary_search.so target/binary_search.c
t1 = time.time()
agent = CLiveAgent(debug=False)
t2 = time.time()
agent.start_server()
t3 = time.time()
agent.initialize()
t4 = time.time()
source_path = os.path.abspath("src/livefromdap/target/binary_search.c")
compiled_path = os.path.abspath("src/livefromdap/target/binary_search.so")
agent.load_code(compiled_path)
t5 = time.time()
return_value, _ = agent.execute(source_path, "binary_search", ["{1,2,3,4,5,6}", "6", "9"])
assert return_value['value'] == "-1"
t6 = time.time()
return_value, _ = agent.execute(source_path, "binary_search", ["{1,2,3,4,5,6}", "6", "4"])
assert return_value['value'] == "3"
t7 = time.time()
agent.stop_server()
print("Agent creation: ", t2 - t1)
print("Server start: ", t3 - t2)
print("Server initialization: ", t4 - t3)
print("Code loading: ", t5 - t4)
print("Execution 1: ", t6 - t5)
print("Execution 2: ", t7 - t6)

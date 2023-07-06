from livefromdap.agent.PythonLiveAgent import PythonLiveAgent
import time

t1 = time.time()
agent = PythonLiveAgent(debug=False)
t2 = time.time()
agent.start_server()
t3 = time.time()
agent.initialize()
t4 = time.time()
agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/binary_search.py")
t5 = time.time()
result, _ = agent.execute("binary_search", ["[1, 2, 3, 4, 5]", "3"])
assert int(result) == 2
t6 = time.time()
result, _ = agent.execute("binary_search", ["[1, 2, 3, 4, 5]", "6"])
assert int(result) == -1
t7 = time.time()
agent.stop_server()
print("Agent creation: ", t2 - t1)
print("Server start: ", t3 - t2)
print("Server initialization: ", t4 - t3)
print("Code loading: ", t5 - t4)
print("Execution 1: ", t6 - t5)
print("Execution 2: ", t7 - t6)

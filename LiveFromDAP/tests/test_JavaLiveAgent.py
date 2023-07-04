from livefromdap.agent.JavaLiveAgent import JavaLiveAgent
import time

t1 = time.time()
agent = JavaLiveAgent(
    target_file="/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/BinarySearch.java",
    target_class_path="/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target",
    target_class_name="BinarySearch",
    target_methods=["binarySearch"],
    debug=False) # Turn this to True to see the debug messages
t2 = time.time()
agent.start_server()
t3 = time.time()
agent.initialize()
t4 = time.time()
agent.load_code()
t5 = time.time()
agent.execute("binarySearch", ["new char[]{'a', 'b'}", "'a'"])
t6 = time.time()
agent.execute("binarySearch", ["new char[]{'a', 'b'}", "'a'"])
t7 = time.time()
agent.stop()
print("Time to create the agent: " + str(t2-t1))
print("Time to start the server: " + str(t3-t2))
print("Time to initialize the server: " + str(t4-t3))
print("Time to load the code: " + str(t5-t4))
print("Time to execute the first time: " + str(t6-t5))
print("Time to execute the second time: " + str(t7-t6))
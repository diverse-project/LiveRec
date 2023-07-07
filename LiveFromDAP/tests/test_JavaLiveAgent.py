from livefromdap.agent.JavaLiveAgent import JavaLiveAgent

def test_java_binary_search():
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/java", "BinarySearch")

    agent.execute("BinarySearch", "binarySearch", ["new char[]{'a', 'b'}", "'a'"])
    agent.execute("BinarySearch", "binarySearch", ["new char[]{'a','b','c','d'}", "'e'"])

    agent.stop_server()

def test_java_bubblesort():
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/java", "BubbleSort")

    agent.execute("BubbleSort", "bubbleSort", ["new int[]{1,2,3,4,5,6}"])
    agent.execute("BubbleSort", "bubbleSort", ["new int[]{6,5,4,3,2,1}"])

    agent.stop_server()

def test_java_fibonnaci():
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/java", "Fibonnaci")

    agent.execute("Fibonnaci", "fibonnaci", ["5"])
    agent.execute("Fibonnaci", "fibonnaci", ["8"])

    agent.stop_server()

def test_java_prime():
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/java", "Prime")

    agent.execute("Prime", "primeInInterval", ["2", "5"])
    agent.execute("Prime", "primeInInterval", ["6", "9"])

    agent.stop_server()

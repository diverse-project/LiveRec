from livefromdap.agent.JavaLiveAgent import JavaLiveAgent

def test_java_binary_search():
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/java", "BinarySearch")

    return_value, _ = agent.execute("BinarySearch", "binarySearch", ["new char[]{'a', 'b'}", "'a'"])
    assert int(return_value) == 0

    return_value, _ = agent.execute("BinarySearch", "binarySearch", ["new char[]{'a','b','c','d'}", "'e'"])
    assert int(return_value) == -1

    agent.stop_server()

def test_java_bubblesort():
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/java", "BubbleSort")

    return_value, _ = agent.execute("BubbleSort", "bubbleSort", ["new int[]{1,2,3,4,5,6}"])
    assert return_value is None

    return_value, _ = agent.execute("BubbleSort", "bubbleSort", ["new int[]{6,5,4,3,2,1}"])
    assert return_value is None

    agent.stop_server()

def test_java_fibonnaci():
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/java", "Fibonnaci")

    return_value, _ = agent.execute("Fibonnaci", "fibonnaci", ["5"])
    assert return_value == "5"
    return_value, _ = agent.execute("Fibonnaci", "fibonnaci", ["8"])
    assert return_value == "21"

    agent.stop_server()

def test_java_prime():
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code("/home/jbdod/CWI/LiveProbes/LiveFromDAP/src/livefromdap/target/java", "Prime")

    return_value, _ = agent.execute("Prime", "primeInInterval", ["2", "5"])
    assert return_value == "3"

    return_value, _ = agent.execute("Prime", "primeInInterval", ["6", "9"])
    assert return_value == "1"

    agent.stop_server()

from livefromdap.agent.CLiveAgent import CLiveAgent
import os
import time

def test_c_binary_search():
    agent = CLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()

    source_path = os.path.abspath("src/livefromdap/target/c/binary_search.c")
    compiled_path = os.path.abspath("src/livefromdap/target/c/binary_search.so")

    agent.load_code(compiled_path)

    return_value, _ = agent.execute(source_path, "binary_search", ["{1,2,3,4,5,6}", "6", "9"])
    assert return_value['value'] == "-1"

    return_value, _ = agent.execute(source_path, "binary_search", ["{1,2,3,4,5,6}", "6", "4"])
    assert return_value['value'] == "3"

    agent.stop_server()

def test_c_bubblesort():
    agent = CLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()

    source_path = os.path.abspath("src/livefromdap/target/c/bubblesort.c")
    compiled_path = os.path.abspath("src/livefromdap/target/c/bubblesort.so")

    agent.load_code(compiled_path)

    _, _ = agent.execute(source_path, "bubblesort", ["{1,2,3,4,5,6}", "6"])
    _, _ = agent.execute(source_path, "bubblesort", ["{6,5,4,3,2,1}", "6"])

    agent.stop_server()
    assert True

def test_c_fibonnaci():
    agent = CLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()

    source_path = os.path.abspath("src/livefromdap/target/c/fibonnaci.c")
    compiled_path = os.path.abspath("src/livefromdap/target/c/fibonnaci.so")

    agent.load_code(compiled_path)

    return_value, _ = agent.execute(source_path, "fibonnaci", ["5"])
    assert return_value['value'] == "5"

    return_value, _ = agent.execute(source_path, "fibonnaci", ["8"])
    assert return_value['value'] == "21"

    agent.stop_server()

def test_c_prime():
    agent = CLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()

    source_path = os.path.abspath("src/livefromdap/target/c/prime.c")
    compiled_path = os.path.abspath("src/livefromdap/target/c/prime.so")

    agent.load_code(compiled_path)

    return_value, _ = agent.execute(source_path, "prime_in_interval", ["2", "5"])
    assert return_value['value'] == "3"

    return_value, _ = agent.execute(source_path, "prime_in_interval", ["6", "9"])
    assert return_value['value'] == "1"

    agent.stop_server()
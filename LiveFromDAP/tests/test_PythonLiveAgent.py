from livefromdap.agent.PythonLiveAgent import PythonLiveAgent
import os

def test_python_binary_search():
    agent = PythonLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()

    agent.load_code(str(os.path.join(os.path.dirname(__file__), "..", "src","livefromdap","target","python", "binary_search.py")))

    result, _ = agent.execute("binary_search", ["[1, 2, 3, 4, 5]", "3"])
    assert int(result) == 2

    result, _ = agent.execute("binary_search", ["[1, 2, 3, 4, 5]", "6"])
    assert int(result) == -1

    agent.stop_server()

def test_python_bubblesort():
    agent = PythonLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()
    agent.load_code(str(os.path.join(os.path.dirname(__file__), "..", "src","livefromdap","target","python", "bubblesort.py")))

    result, _ = agent.execute("bubblesort", ["[1, 2, 3, 4, 5, 6]"])
    assert result == "[1, 2, 3, 4, 5, 6]"

    result, _ = agent.execute("bubblesort", ["[6, 5, 4, 3, 2, 1]"])
    assert result == "[1, 2, 3, 4, 5, 6]"

    agent.stop_server()

def test_python_fibonnaci():
    agent = PythonLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()
    agent.load_code(str(os.path.join(os.path.dirname(__file__), "..", "src","livefromdap","target","python", "fibonnaci.py")))
    result, _ = agent.execute("fibonnaci", ["5"])
    assert int(result) == 5

    result, _ = agent.execute("fibonnaci", ["8"])
    assert int(result) == 21

    agent.stop_server()

def test_python_prime():
    agent = PythonLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()
    agent.load_code(str(os.path.join(os.path.dirname(__file__), "..", "src","livefromdap","target","python", "prime.py")))
    result, _ = agent.execute("prime_in_interval", ["2", "5"])
    assert int(result) == 3

    result, _ = agent.execute("prime_in_interval", ["6", "9"])
    assert int(result) == 1

    agent.stop_server()


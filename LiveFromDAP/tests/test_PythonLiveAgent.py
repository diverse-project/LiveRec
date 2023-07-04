from livefromdap.agent.PythonLiveAgent import PythonLiveAgent


def test_python_live_agent():
    agent = PythonLiveAgent(
        target_path="src/livefromdap/target/binary_search.py", 
        target_method="binary_search",
        debug=False)
    agent.start_server()
    agent.initialize()
    agent.load_code()
    print("Test 1")
    result, _ = agent.execute("binary_search", ["[1, 2, 3, 4, 5]", "3"])
    assert int(result) == 2
    print("Test 2")
    result, _ = agent.execute("binary_search", ["[1, 2, 3, 4, 5]", "6"])
    assert int(result) == -1
    print("Test reload")
    agent.load_code()
    result, _ = agent.execute("binary_search", ["[1, 2, 3, 4, 5]", "6"])
    assert int(result) == -1
    agent.stop()
    return

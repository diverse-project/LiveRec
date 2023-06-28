from livefromdap.agent.PythonLiveAgent import PythonLiveAgent as Pyt


def test_python_live_agent():
    agent = Pyt(
        runner_path="src/livefromdap/runner/runner.py", 
        target_path="src/livefromdap/target/binary_search.py", 
        target_method="binary_search",
        debug=False)
    agent.load_code()
    print("Test 1")
    result, _ = agent.execute(["[1, 2, 3, 4, 5]", "3"])
    assert int(result) == 2
    print("Test 2")
    result, _ = agent.execute(["[1, 2, 3, 4, 5]", "6"])
    assert int(result) == -1
    print("Test reload")
    agent.load_code()
    result, _ = agent.execute(["[1, 2, 3, 4, 5]", "6"])
    assert int(result) == -1

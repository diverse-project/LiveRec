from livefromdap.agent.CLiveAgent import CLiveAgent

def test_CLiveAgent():
    # Compile command : gcc -g -fPIC -shared -o target/binary_search.so target/binary_search.c
    agent = CLiveAgent(
        runner_path="src/livefromdap/runner/runner.c",
        target_path="src/livefromdap/target/binary_search.c",
        target_method="binary_search",
        runner_path_exec="src/livefromdap/runner/runner",
        target_path_exec="src/livefromdap/target/binary_search.so",
        debug=False)
    agent.load_code()
    return_value, _ = agent.execute(["{1,2,3,4,5,6}", "6", "9"])
    assert return_value['value'] == "-1"
    return_value, _ = agent.execute(["{1,2,3,4,5,6}", "6", "4"])
    assert return_value['value'] == "3"
    agent.stop()
    return
from livefromdap.agent.CLiveAgent import CLiveAgent

def test_CLiveAgent():
    # Compile command : gcc -g -fPIC -shared -o target/binary_search.so target/binary_search.c
    agent = CLiveAgent(
        target_file="src/livefromdap/target/binary_search.c",
        target_methods=["binary_search"],
        debug=False)
    agent.start_server()
    agent.initialize()
    agent.load_code()
    return_value, _ = agent.execute("binary_search", ["{1,2,3,4,5,6}", "6", "9"])
    assert return_value['value'] == "-1"
    return_value, _ = agent.execute("binary_search", ["{1,2,3,4,5,6}", "6", "4"])
    assert return_value['value'] == "3"
    agent.stop()
    return
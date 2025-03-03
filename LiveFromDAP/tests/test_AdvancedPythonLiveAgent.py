from livefromdap.agent.AdvancedPythonLiveAgent import AdvancedPythonLiveAgent
import os

def test_python_binary_search():
    agent = AdvancedPythonLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()

    agent.set_source_path(str(os.path.join(os.path.dirname(__file__), "..", "src","livefromdap","target","python","runtime_data","main.py")))

    data_dict = '{"locals": {"x": 1}, "globals": {}}'

    result, _ = agent.execute("f", data_dict)
    assert int(result) == 49995000

    mock_data_path = str(os.path.join(os.path.dirname(__file__), "..", "src","livefromdap","target","python","runtime_data","lib.py.jsonl"))
    agent.add_mocked_data(mock_data_path)
    result, _ = agent.execute("f", data_dict)
    assert int(result) == 1

    agent.stop_server()

if "__main__" in __name__:
    test_python_binary_search()
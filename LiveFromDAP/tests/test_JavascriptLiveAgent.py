from livefromdap.agent.JavascriptLiveAgent import JavascriptLiveAgent
import os

def test_javascript_binary_search():
    agent = JavascriptLiveAgent(debug=True)
    agent.start_server()
    agent.initialize()

    path = str(os.path.join(os.path.dirname(__file__), "..", "src","livefromdap","target","javascript", "binary_search.js"))

    agent.load_code(path)

    result, _ = agent.execute(path, "binary_search", ["[1, 2, 3, 4, 5]", "3"])
    assert int(result) == 2

    result, _ = agent.execute(path, "binary_search", ["[1, 2, 3, 4, 5]", "6"])
    assert int(result) == -1

    agent.stop_server()

if __name__ == "__main__":
    test_javascript_binary_search()



from prettyprinter.CPrettyPrinter import CPrettyPrinter
from livefromdap.agent.CLiveAgent import CLiveAgent

def test_CPrettyPrinter():
    agent = CLiveAgent(
        runner_path="src/livefromdap/runner/runner.c",
        target_path="src/livefromdap/target/binary_search.c",
        target_method="binary_search",
        runner_path_exec="src/livefromdap/runner/runner",
        target_path_exec="src/livefromdap/target/binary_search.so",
        debug=False)
    agent.load_code()
    return_value, stacktrace = agent.execute(["{1,2,3,4,5,6}", "6", "9"])
    assert return_value['value'] == "-1"
    agent.stop()
    printer = CPrettyPrinter("src/livefromdap/target/binary_search.c","binary_search")
    print("== Pretty print ==")
    print(printer.pretty_print(stacktrace, return_value=return_value['value']))
    

if __name__ == '__main__':
    test_CPrettyPrinter()
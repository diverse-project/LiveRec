import subprocess
from livefromdap.agent.CLiveAgent import CLiveAgent
from livefromdap.agent.JavaLiveAgent import JavaLiveAgent
from livefromdap.agent.PythonLiveAgent import PythonLiveAgent
import os

def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    return process.returncode

def test_c_binary_search_reload():
    initial_code = """
int binary_search(int arr[], int length, int target) {
    int left = 0;
    int right = length - 1;
    while (left <= right) {
        int mid = (left + right) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}
    """

    modified_code = """
int binary_search(int arr[], int length, int target) {
    int left = 0;
    int right = length - 1;
    while (left <= right) {
        int mid = (left + right) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -2;
}
    """

    with open("tmp/binary_search.c", "w") as f:
        f.write(initial_code)
    execute_command("gcc -g -shared -fPIC -o tmp/binary_search.so tmp/binary_search.c")

    agent = CLiveAgent(debug=False)
    agent.start_server()
    agent.initialize()

    source_path = os.path.abspath("tmp/binary_search.c")
    compiled_path = os.path.abspath("tmp/binary_search.so")

    agent.load_code(compiled_path)

    return_value, _ = agent.execute(source_path, "binary_search", ["{1,2,3,4,5,6}", "6", "9"])
    assert return_value['value'] == "-1"

    with open("tmp/binary_search.c", "w") as f:
        f.write(modified_code)
    execute_command("gcc -g -shared -fPIC -o tmp/binary_search.so tmp/binary_search.c")

    agent.load_code(compiled_path)

    return_value, _ = agent.execute(source_path, "binary_search", ["{1,2,3,4,5,6}", "6", "9"])
    assert return_value['value'] == "-2"

    agent.stop_server()

def test_java_binary_search_reload():
    initial_code = """
public class BinarySearch {
    public static int binarySearch(char[] array, char key) throws InterruptedException {
        int low = 0;
        int high = array.length - 1;
        while (low <= high) {
            int mid = (low + high) / 2;
            char value = array[mid];
            if (value < key) {
                low = mid + 1;
            } else if (value > key) {
                high = mid - 1;
            } else {
                return mid;
            }
        }
        return -1;
    }
}
    """

    modified_code = """
public class BinarySearch {
    public static int binarySearch(char[] array, char key) throws InterruptedException {
        int low = 0;
        int high = array.length - 1;
        while (low <= high) {
            int mid = (low + high) / 2;
            char value = array[mid];
            if (value < key) {
                low = mid + 1;
            } else if (value > key) {
                high = mid - 1;
            } else {
                return mid;
            }
        }
        return -2;
    }
}
    """

    with open("tmp/BinarySearch.java", "w") as f:
        f.write(initial_code)
    #compile the file
    execute_command("javac -g -d tmp tmp/BinarySearch.java")
    old_bytecode = None
    with open("tmp/BinarySearch.class", "rb") as f:
        old_bytecode = f.read()

    code_path = os.path.abspath("tmp")
    agent = JavaLiveAgent(debug=False) # Turn this to True to see the debug messages

    agent.start_server()
    agent.initialize()
    agent.load_code(code_path, "BinarySearch")

    result, _ = agent.execute("BinarySearch", "binarySearch", ["new char[]{'a', 'b', 'c', 'd', 'e'}", "'f'"])
    assert result == "-1"

    with open("tmp/BinarySearch.java", "w") as f:
        f.write(modified_code)
    execute_command("javac -g -d tmp tmp/BinarySearch.java")
    new_bytecode = None
    with open("tmp/BinarySearch.class", "rb") as f:
        new_bytecode = f.read()
    # wait for the file to be compiled
    # Check if the bytecode has changed
    assert old_bytecode != new_bytecode

    agent.load_code(code_path, "BinarySearch")

    result, _ = agent.execute("BinarySearch", "binarySearch", ["new char[]{'a', 'b', 'c', 'd', 'e'}", "'f'"])
    assert result == "-2"
    agent.stop_server()
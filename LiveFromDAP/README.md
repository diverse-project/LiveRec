# Live From DAP

This package provides a set of tools for working with live data obtained from the [DAP]().

## Installation

```bash
git clone https://github.com/cwi-swat/LiveProbes/
cd LiveProbes/LiveFromDAP
python -m venv venv # Create a virtual environment
source venv/bin/activate # Activate the virtual environment
pip install -r requirements.txt # Install the requirements
pip install -e . # Install the package
chmod +x install.sh
./install.sh # Install the debug servers
```

### Getting the debug servers

The script `get_debug_servers.sh` can be used to download the debug servers for the different languages.

#### Python

The debug server for Python is included in the debugpy package installed as requirement.

#### C

The debug server for C is `OpenDebugAD7` and can be be easily obtained in the Visual Studio Code extension.
If you want to install it manually : 

- Download the [Visual Studio Code extension vsix](https://github.com/microsoft/vscode-cpptools/releases/)
- Extract the vsix file
- Copy the `extension/debugAdapters/bin` folder to `src/livefromdap/bin/` and rename it `OpenDebugAD7` (you should have `src/livefromdap/bin/OpenDebugAD7/OpenDebugAD7`)

If you want to use the debug server from the Visual Studio Code extension, you can set the `debug_server_path` parameter to the correct path when creating the agent.

#### Java

The debug server for Java rely on [JDT Language Server](https://github.com/eclipse/eclipse.jdt.ls) and [Java Debug Server](https://github.com/Microsoft/java-debug)

For manual installation you can recompile from source or download the binaries:
- Download [JDT LS binary](https://download.eclipse.org/jdtls/milestones/1.24.0/)
- Download [Java debug Visual Studio Code extension vsix](https://github.com/microsoft/vscode-java-debug/releases/)
- Extract the vsix file
- Copy the `extension/server/com.microsoft.java.debug.plugin-VERSION.jar` file to `src/livefromdap/bin/` and rename it `com.microsoft.java.debug.plugin.jar`
- Copy the `jdt-language-server-VERSION` directory to `src/livefromdap/bin/` and rename it `jdt-language-server`


## Usage

```python
from livefromdap import CLiveAgent
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
```

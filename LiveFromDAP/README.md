# Live From DAP

This package provides a set of tools for working with live data obtained from the [DAP]().

## Installation

```bash
git clone https://github.com/cwi-swat/LiveProbes/
cd LiveProbes/LiveFromDAP
python -m venv venv # Create a virtual environment
source venv/bin/activate # Activate the virtual environment
pip install -e . # Install the package
```

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

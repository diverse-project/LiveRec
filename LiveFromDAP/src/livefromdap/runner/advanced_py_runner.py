from collections import defaultdict
from typing import Any
import jsonpickle
import os
import inspect
import sys

class CustomMatchingDict:
    def __init__(self, match_function=None):
        self._data = []  # liste de tuples (clé_dict, valeur)
        self._match_function = match_function or self._default_match
        
    def _default_match(self, key1, key2):
        for k, v1 in key1.items():
            v2 = key2.get(k)
            eq_method = v1.__class__.__eq__
            if eq_method is object.__eq__:
                if not isinstance(v2, type(v1)):
                    return False
            else:
                if not v1 == v2:
                    return False
        return True
    
    def __setitem__(self, key, value):
        for i, (existing_key, _) in enumerate(self._data):
            if self._match_function(existing_key, key):
                self._data[i] = (key, value)
                return
        self._data.append((key, value))
        
    def __getitem__(self, key):
        for existing_key, value in self._data:
            if self._match_function(key, existing_key): # order is important because of the default matching function
                return value
        self._data.append((key, []))
        return self._data[-1][1]
    
    def match_closest(self, key):
        dist : list[int] = []
        for existing_key, value in self._data:
            # calculate the distance between the key and the existing key
            dist.append(self.distance(key, existing_key))
        # take the argmin of the distance (could return multiple if there is a tie)
        min_dist = min(dist)
        min_dist_indices = [index for index, value in enumerate(dist) if value == min_dist]
        return [self._data[i][1] for i in min_dist_indices]
    
    def distance(self, key1, key2):
        match type(key1):
            case int():
                return abs(key1 - key2)
            case float():
                return abs(key1 - key2)
            case str():
                return sum(1 for c1, c2 in zip(key1, key2) if c1 != c2) # Could use other string distance metrics
            case list():
                return sum(self.distance(a, b) for a, b in zip(key1, key2))
            case dict():
                s = 0
                for k in key1.keys():
                    if k in key2.keys():
                        s += self.distance(key1[k], key2[k])
                return s
            case _:
                raise 0
        
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
        
source_path = None
reexecute = False
method_name = None
method_args = None
reload_code = False
mocked_functions = defaultdict(lambda: defaultdict(CustomMatchingDict))
match_closest = False

def set_match_closest(match_closestp : bool):
    global match_closest
    match_closest = match_closestp

def compute_mocked_result(function, file : str, args : tuple[Any], kwargs : dict[str, Any]):
    global mocked_functions, match_closest
    function_name = function.__name__
    
    # Retrieve the function object from its name.
    sig = inspect.signature(function)

    # Build a dict of argument name -> argument value, starting with positional args.
    call_locals = {}
    arg_iter = iter(args)
    for param_name, param in sig.parameters.items():
        # Skip *args and **kwargs types (if any).
        if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            try:
                call_locals[param_name] = next(arg_iter)
            except StopIteration:
                # If we run out of positional args, break or handle default values as needed.
                break

    # Merge in any named keyword args.
    for k, v in kwargs.items():
        call_locals[k] = v
    # Compare call_locals with stored execution histories.
    possible_results = mocked_functions[file][function_name][call_locals]
    if len(possible_results) == 0:
        if match_closest:
            possible_results = mocked_functions[file][function_name].match_closest(call_locals)
            if len(possible_results) == 0:
                return False, None
            else:
                return True, possible_results[-1]["return_value"]
        else:
            return False, None
    else:
        return True, possible_results[-1]["return_value"]

def mock(func, file : str):
    """
    A decorator that allows a function to be mocked.
    It simply returns the original function without any modification.
    """
    def wrapper(*args, **kwargs):
        is_mockable, mock_res = compute_mocked_result(func, file, args, kwargs)
        if is_mockable:
            return mock_res  # Return the mock result directly
        else:
            return func(*args, **kwargs)
    return wrapper

def add_mocked_data(file_path : str):
    global mocked_functions, reload_code
    with open(file_path, "r") as file:
        for line in file:
            if line.strip() == "":
                continue
            data = jsonpickle.decode(line) # type: ignore
            mocked_functions[data["file"]][data["function"]][data["locals"]].append(data)
    reload_code = True



def apply_mock_decorators():
    global mocked_functions
    for file_name in mocked_functions.keys():
        for module in sys.modules.values():
            if hasattr(module, "__file__") and file_name == module.__file__:
                for function_name in mocked_functions[file_name].keys():
                    original_func = module.__dict__[function_name]
                    mocked_func = mock(original_func, file_name)
                    module.__dict__[function_name] = mocked_func

def set_reload_code(reload_codep : bool):
    global reload_code
    reload_code = reload_codep

def set_reexecute(reexecutep : bool):
    global reexecute
    reexecute = reexecutep

def set_source_path(source_pathp : str):
    global source_path, reload_code
    source_dir = os.path.dirname(source_pathp)
    os.chdir(source_dir)
    sys.path.append(source_dir)
    source_path = source_pathp
    reload_code = True

def load_data(method_namep : str, data : str):
    global method_name, method_args, reexecute
    method_name = method_namep
    datas : dict = jsonpickle.decode(data) # type: ignore
    local_vars : dict = datas["locals"]
    global_vars : dict = datas["globals"]
    globals().update(global_vars)
    method = eval(method_name) # type: ignore
    method_args = [local_vars[k] for k in method.__code__.co_varnames if k in local_vars]
    reexecute = True

if "__main__" in __name__:
    while True:  
        if reload_code:
            try:
                if source_path is not None:
                    with open(source_path, "r") as source_file:
                        code = compile(source_file.read(), source_path, "exec")
                        exec(code, globals())
            except Exception as e:
                raise e
            apply_mock_decorators()
            reload_code = False
        if reexecute:
            res = None
            try:
                method = eval(method_name) # type: ignore
                res = method(*method_args)
            except Exception as e:
                raise e
            reexecute = False

from typing import Any
import jsonpickle
import os
import ast
import inspect
_no_monitoring = True
source_path = None
reexecute = False
method_name = None
method_args = None
reload_code = False
mocked_functions = {}

class FunctionAndClassExtractor(ast.NodeVisitor):
    def __init__(self, mocked_functions_names : list[str] = []):
        self.definitions = []
        self.mocked_functions_names = mocked_functions_names
        self.inside_class = False

    def visit_Import(self, node):
        self.definitions.append(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.definitions.append(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name in self.mocked_functions_names:
            decorator = ast.Name(id='mock', ctx=ast.Load(), lineno=node.lineno-1, col_offset=node.col_offset+1, end_lineno=node.lineno-1, end_col_offset=node.col_offset+5)
            # add the decorator to the node, check if the decorator is already there
            if not any(isinstance(d, ast.Name) and d.id == 'mock' for d in node.decorator_list):
                node.decorator_list.append(decorator)
        if not self.inside_class:
            self.definitions.append(node)

    def visit_ClassDef(self, node):
        self.inside_class = True
        self.generic_visit(node)
        self.inside_class = False
        self.definitions.append(node)

def smart_equals(a: Any, b: Any) -> bool:
    """
    Smart equality comparison that:
    1. Uses __eq__ if well-defined (not object's default)
    2. Falls back to type checking if __eq__ is the default object implementation
    """
    # If either object is None, use direct comparison
    if a is None or b is None:
        return a is b
    
    # Get the __eq__ method from the object's class
    eq_method = a.__class__.__eq__
    
    # Check if it's the default object.__eq__ implementation
    if eq_method is object.__eq__:
        # If it's the default implementation, just compare types
        return isinstance(a, type(b))
    
    # Otherwise use the custom __eq__ implementation
    return a == b

def compute_mocked_result(function, args : tuple[Any], kwargs : dict[str, Any]):
    global mocked_functions
    function_name = function.__name__
    all_history : list[tuple[dict[str, Any], Any]]  = jsonpickle.decode(mocked_functions[function_name]) # type: ignore
    
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
    for exec_locals, exec_result in all_history:
        exec_keys = set(exec_locals.keys())
        intersection = set(call_locals.keys()).intersection(exec_keys)
        break_loop = False
        for k in intersection:
            if not smart_equals(call_locals[k], exec_locals[k]):
                break_loop = True
                break
        if not break_loop:
            return True, exec_result
    return False, None # Default to the last picked result

def mock(func):
    """
    A decorator that allows a function to be mocked.
    It simply returns the original function without any modification.
    """
    def wrapper(*args, **kwargs):
        is_mockable, mock_res = compute_mocked_result(func, args, kwargs)
        if is_mockable:
            return mock_res  # Return the mock result directly
        else:
            return func(*args, **kwargs)
    return wrapper

def extract_exec_code(code : str):
    tree = ast.parse(code)
    extractor = FunctionAndClassExtractor(list(mocked_functions.keys()))
    extractor.visit(tree)
    new_tree = ast.Module(body=extractor.definitions)
    return new_tree

def add_mocked_functions(mocked_functionsp : str, data: str):
    global mocked_functions, reload_code
    mocked_functions[mocked_functionsp] = data
    reload_code = True

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
    source_path = source_pathp
    reload_code = True

def load_data(method_namep : str, data : dict):
    global method_name, method_args, reexecute
    method_name = method_namep
    datas : dict = data # type: ignore
    local_vars : dict = jsonpickle.decode(datas["locals"]) # type: ignore
    global_vars : dict = jsonpickle.decode(datas["globals"]) # type: ignore
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
                        code = compile(extract_exec_code(source_file.read()), source_path, "exec")
                        exec(code, globals())
            except Exception as e:
                raise e
            reload_code = False
        if reexecute:
            try:
                method = eval(method_name) # type: ignore
                res = method(*method_args)
            except Exception as e:
                raise e
            reexecute = False

import jsonpickle

method = None
method_name = None
method_args = None
import_file = None
reexecute = False

def set_import(import_fromp : str):
    global import_file
    import_file = import_fromp

def set_method(import_methodp : str, method_argsp : list):
    global method_name, method_args
    method_name = import_methodp
    method_args = method_argsp

def set_method_real(import_methodp : str, method_argsp : str):
    global method_name, method_args, reexecute
    method_name = import_methodp
    all_vars : dict = jsonpickle.decode(method_argsp) # type: ignore
    method = eval(method_name)
    # only keep variable in local that are in the varnames
    method_args = [all_vars[k] for k in method.__code__.co_varnames if k in all_vars]
    reexecute = True

if "__main__" in __name__:
    while True:
        if import_file is not None:
            try:
                with open(import_file, "rb") as source_file:
                    code = compile(source_file.read(), import_file, "exec")
                exec(code)
            except Exception as e:
                pass
            import_file = None     
        if reexecute:
            try:
                method = eval(method_name)
                res = method(*method_args)
            except Exception as e:
                pass
            reexecute = False

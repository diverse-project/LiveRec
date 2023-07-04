method = None
method_args = None
import_file = None
import_method = None

def set_import(import_fromp, import_methodp):
    global import_file, import_method
    import_file = import_fromp
    import_method = import_methodp

def set_method(method_argsp):
    global method_args
    method_args = method_argsp

def execution():
    global method, method_args, import_file, import_method
    if import_file is not None:
        # Reload moduel if already loaded
        with open(import_file, "rb") as source_file:
            code = compile(source_file.read(), import_file, "exec")
        exec(code)
        method = eval(import_method)
        import_file = None
        import_method = None
    if method is not None and method_args is not None:
        res = method(*method_args)
        method_args = None

if "__main__" in __name__:
    while True:
        execution()
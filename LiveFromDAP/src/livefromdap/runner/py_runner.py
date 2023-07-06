method = None
method_name = None
method_args = None
import_file = None

def set_import(import_fromp):
    global import_file
    import_file = import_fromp

def set_method(import_methodp, method_argsp):
    global method_name, method_args
    method_name = import_methodp
    method_args = method_argsp

if "__main__" in __name__:
    while True:
        if import_file is not None:
            with open(import_file, "rb") as source_file:
                code = compile(source_file.read(), import_file, "exec")
            exec(code)
            import_file = None     
        if method_name is not None and method_args is not None:
            method = eval(method_name)
            res = method(*method_args)
            method_args = None
            method_name = None

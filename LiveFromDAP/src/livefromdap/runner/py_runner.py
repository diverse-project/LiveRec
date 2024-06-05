import ast

method = None
method_name = None
method_args = None
import_file = None

def exec_then_eval(code, _src_file, _globals = {}, _locals = {}):
    block = ast.parse(code, mode='exec')
    last = block.body.pop()
    exec(compile(block, _src_file, mode="exec"), _globals, _locals)

    try:
        result_node = ast.Expression(last.value)
        return eval(compile(result_node, _src_file, mode='eval'), _globals, _locals)
    except:
        return eval(compile(last, _src_file, mode='eval'), _globals, _locals)

def polyglotEval(i, j):
    src_file = None
    ret = -1
    while src_file is not None:
        with open(src_file, "rb") as source_file:
            code = source_file.read()
        intermediate_ret = exec_then_eval(code, src_file)
        src_file = None
    return ret

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
            exec_result = exec_then_eval(code)
            import_file = None     
        if method_name is not None and method_args is not None:
            try:
                method = eval(method_name)
                res = method(*method_args)
            except Exception as e:
                pass
            method_args = None
            method_name = None

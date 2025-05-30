import sys, os
method = None
method_name = None
method_args = None
import_file = None

def probe(line, global_dict, local_dict, expr):
    try:
        ret = eval(expr, globals=global_dict, locals=local_dict)
    except Exception as e:
        pass
    return

# TODO: update breakpoint lines in agent
class Replacement:

    table = {}

    def __init__(self, val_list):
        self.val_list = val_list
        self.index = 0

    def create_replacement(path, line, val_list):
        replacement_key = (path, line)
        if replacement_key in Replacement.table.keys():
            return Replacement.table[replacement_key]
        replace = Replacement(val_list)
        Replacement.table[replacement_key] = replace

    def next_val(self):
        result = self.val_list[self.index]
        if len(self.val_list) - 1 > self.index:
            self.index += 1
        return result



def set_import(import_fromp):
    global import_file
    sys.path.append(os.path.dirname(import_fromp))
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
            try:
                method = eval(method_name)
                res = method(*method_args)
            except Exception as e:
                pass
            method_args = None
            method_name = None

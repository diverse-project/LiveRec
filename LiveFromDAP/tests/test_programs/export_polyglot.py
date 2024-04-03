#@foo(1,2)
def foo(a, b):
    polyglotExport("b", b)
    t = polyglotEval("js", "var x = polyglotImport('b') + 3; x")
    return a + b + t

def polyglotEval(i, j):
    return -1

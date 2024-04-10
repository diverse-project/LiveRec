#@foo(1,2)
def foo(a, b):
    polyglotEval("js", "var x = 4; polyglotExport('x', x)")
    t = polyglotImport("x")
    return a + b + t


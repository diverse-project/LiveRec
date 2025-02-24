#@foo(1,2)
def foo(a, b):
    t = polyglotEval("js", "var x = 2+2; x")
    return a + b + t


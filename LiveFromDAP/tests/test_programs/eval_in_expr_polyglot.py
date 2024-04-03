#@foo(1,2)
def foo(a, b):
    polyglotEval("js", "var x = 1; x = x + 3;")
    return a + b + polyglotEval("js", "x")


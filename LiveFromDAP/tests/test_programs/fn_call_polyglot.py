#@foo(1,2)
def foo(a, b):
    t = polyglotEval("js", "var x = 1; x")
    for i in range(0, 5):
        t = bar()
    return a + b + t

def bar():
    polyglotEval("js", "x = x + 1; x")


#@foo(1,2)
def foo(a, b):
    t = polyglotEval("js", "var x = 1; x")
    for i in range(0, 5):
        t = bar(t)
    return a + b + t

#@bar(3)
def bar(x):
    r = x * polyglotEval("js", "x = x + 1; x")
    return r



#@ex1:foo(1,2)
#@ex2:foo(1,3)
def foo(a, b):
    t = bar(a)
    #@ex1:probe : t
    for i in range(0, 5):
        t = t + 1
        #@ex1:probe : t if £ t % 2 == 0 £
    return a + b + t

#@ex3:bar(3)
#@ex4:bar(1)
def bar(x):
    polyglotEval("js", "/test/square.js")
    r = polyglotEval("js", "square(2 + 3)")
    #@ex2:probe : r
    #@ex1:probe JS.square: t1
    return r*2
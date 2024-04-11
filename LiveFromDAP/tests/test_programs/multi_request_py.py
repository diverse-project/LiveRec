#@foo(1,2)
#@foo(1,3)
def foo(a, b):
    t = bar(a)
    for i in range(0, 5):
        t = t + 1
    return a + b + t

#@bar(3)
#@bar(1)
def bar(x):
    r = x * 2
    return r


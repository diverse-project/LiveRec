import lib # you can use linear_function and linear_search from lib.py which has been instrumented by PyMonitor

def f(x : int) -> int:
    a = x+1
    res = lib.linear_function(x)
    return res

def g(arr : list[int], target : int) -> int:
    return lib.linear_search(arr, target)


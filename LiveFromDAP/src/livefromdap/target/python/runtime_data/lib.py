import monitoringpy

@monitoringpy.pymonitor
def linear_search(arr, target):
    for i, value in enumerate(arr):
        if value == target:
            return i
        
@monitoringpy.pymonitor
def linear_function(x):
    a = 0
    for i in range(10000*x):
        a += i
    return a

if __name__ == "__main__":
    monitoringpy.init_monitoring(output_file="lib.py.jsonl")
    linear_search([1, 2, 3, 4, 5], 3)
    linear_function(1)
    linear_function(10)
['a', 'b', 'c', 'd', 'e', 'f'], 'd';None;false
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    mid = (left + right) // 2
    value = arr[mid]
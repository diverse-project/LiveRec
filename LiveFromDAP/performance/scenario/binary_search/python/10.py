['a', 'b', 'c', 'd', 'e', 'f'], 'a';0;false
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while True:
        mid = (left + right) // 2
        value = arr[mid]
        
        if value < target:
            left = mid + 1
        elif value > target:
            right = mid - 1
        else:
            return mid
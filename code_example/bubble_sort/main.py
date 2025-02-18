from monitoringpy import init_monitoring
import random
init_monitoring()


def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


if __name__ == "__main__":
    arr = [random.randint(0, 100) for _ in range(10)]
    bubble_sort(arr)
    print(arr)
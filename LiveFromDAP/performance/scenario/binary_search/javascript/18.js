['a', 'b', 'c', 'd', 'e', 'f'], 'g';-1;true
function binary_search(arr, target){
    var low = 0;
    var high = arr.length - 1;
    while (low <= high) {
        var mid = Math.floor((low + high) / 2);
        var value = arr[mid];

        if (value < target) {
            low = mid + 1;
        }
        else if (value > target) {
            high = mid - 1;
        }
        else {
            return mid;
        }
    }
    return -1;
}
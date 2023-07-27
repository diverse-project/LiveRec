['a', 'b', 'c', 'd', 'e', 'f'], 'b';1;false
function binary_search(arr, target){
    var low = 0;
    var high = arr.length - 1;
    while (true) {
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
}
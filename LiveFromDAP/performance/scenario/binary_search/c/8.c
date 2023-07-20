{'a', 'b', 'c', 'd', 'e', 'f'}, 6, 'c';2;false
int binary_search(char arr[], int length, char target) {
    int left = 0;
    int right = length - 1;
    
    int mid = (left + right) / 2;
    char value = arr[mid];

    if(value < target) {
        left = mid + 1;
    } else if(value > target) {
        right = mid - 1;
    } else {
        return mid;
    }
    return -1; // random value otherwise
}
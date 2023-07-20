{'a', 'b', 'c', 'd', 'e', 'f'}, 6, 'g';-2;true
int binary_search(char arr[], int length, char target) {
    int left = 0;
    int right = length - 1;
    
    while(left <= right){
        int mid = (left + right) / 2;
        char value = arr[mid];

        if(value < target) {
            left = mid + 1;
        } else if(value > target) {
            right = mid - 1;
        } else {
            return mid;
        }
    }
    return -2; // random value otherwise
}
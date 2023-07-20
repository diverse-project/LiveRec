{'a', 'b', 'c', 'd', 'e', 'f'}, 6, 'f';5;false
int binary_search(char arr[], int length, char target) {
    int left = 0;
    int right = length - 1;
    
    while(1){
        
        int mid = (left + right) / 2;
        char value = arr[mid];

        if(value < target) {
            left = mid + 1;
        } else if (value > target) {
            right = mid - 1;
        } else {
            return mid;
        }
    }
}
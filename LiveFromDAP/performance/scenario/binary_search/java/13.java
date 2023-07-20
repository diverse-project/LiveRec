new char[]{'a','b','c','d','e','f'}, 'd';3;false
public class BinarySearch {
    public static int binarySearch(char[] array, char key) {
        int low = 0;
        int high = array.length - 1;

        while(true){
            int mid = (low + high) / 2;
            char value = array[mid];
            
            if (value < key) {
                low = mid + 1;
            } else if (value > key) {
                high = mid - 1;
            } else {
                return mid;
            }
        }
    }
}
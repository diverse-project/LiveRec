package samples;

public class BretVictorExample {
    public int binarySearch(char[] array, char key) throws InterruptedException {
        // test
        int low = 0;
        int high = array.length - 1;
        while (low <= high) {
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
        return -1;
    }

    public static void main(String[] args) throws InterruptedException {
        BretVictorExample bve = new BretVictorExample();
        char[] array = {'a', 'b', 'c', 'd', 'e', 'f', 'g'};
        char key = 'd';
        int result = bve.binarySearch(array, key);
        System.out.println(result);
    }

}

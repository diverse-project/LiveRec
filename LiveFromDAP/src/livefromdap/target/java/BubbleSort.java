public class BubbleSort {
    public static void bubbleSort(char[] array) throws InterruptedException {
        int n = array.length;
        boolean swapped = true;
        while (swapped) {
            swapped = false;
            for (int i = 1; i < n; i++) {
                char a = array[i - 1];
                char b = array[i];
                if (a > b) {
                    array[i - 1] = b;
                    array[i] = a;
                    swapped = true;
                }
            }
        }
    }
    
}

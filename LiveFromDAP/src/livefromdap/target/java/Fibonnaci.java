public class Fibonnaci {
    public static int fibonnaci(int n) throws InterruptedException {
        if (n <= 1) {
            return n;
        }
        return fibonnaci(n - 1) + fibonnaci(n - 2);
    }
}

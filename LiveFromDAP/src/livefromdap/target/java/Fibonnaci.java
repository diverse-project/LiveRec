public class Fibonnaci {
    public int fibonnaci(int n) throws InterruptedException {
        if (n <= 1) {
            return n;
        }
        return fibonnaci(n - 1) + fibonnaci(n - 2);
    }
}

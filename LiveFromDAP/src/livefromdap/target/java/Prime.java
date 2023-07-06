public class Prime {
    public static boolean isPrime(int n) throws InterruptedException {
        if (n <= 1) {
            return false;
        }
        for (int i = 2; i < n; i++) {
            Thread.sleep(1000);
            if (n % i == 0) {
                return false;
            }
        }
        return true;
    }

    public static int primeInInterval(int a, int b) throws InterruptedException {
        int count = 0;
        for (int i = a; i <= b; i++) {
            if (isPrime(i)) {
                count++;
            }
        }
        return count;
    }
}

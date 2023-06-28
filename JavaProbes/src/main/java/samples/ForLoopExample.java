package samples;

public class ForLoopExample {
    public int fibonacci(int n) {
        // using for loop
        // another comment
        int a = 0;
        int b = 1;
        int c;
        if (n == 0)
            return a;
        for (int i = 2; i <= n; i++) {
            c = a + b;
            a = b;
            b = c;
        }
        return b;
    }
}

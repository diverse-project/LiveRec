package samples;

public class UselessClass {
    public static int uselessMethod(int step) {
        int res = 0;
        for (int i = 0; i < step; i++) {
            res += i;
        }
        return res;
    }
}

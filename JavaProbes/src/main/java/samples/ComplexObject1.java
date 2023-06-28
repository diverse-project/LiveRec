package samples;

public class ComplexObject1 {

    public int complexObject1(boolean a, byte b, char c, short d, int e, long f, float g, double h, String i, int[] j) {
        int len = i.length();
        if (a) {
            // Convert b to a char
            char bChar = (char) b;
            if (b == c){
                // sum d e f g and h
                int sum = d + e + (int) f + (int) g + (int) h;
                while (sum > 0) {
                    len++;
                    sum--;
                }
            }
        }
        return len;
    }
}

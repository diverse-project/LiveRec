package debugger;

import static java.lang.Class.forName;

public class DebugAgent {

    public void loadClass(String className) {
        ClassLoader classLoader = ClassLoader.getSystemClassLoader();
        try {
            forName(className, true, classLoader);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    public static void main(String[] args) {
        while (true) {}
    }
}

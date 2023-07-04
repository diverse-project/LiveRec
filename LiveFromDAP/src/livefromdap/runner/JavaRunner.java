import java.lang.reflect.Method;
import static java.lang.Class.forName;

public class JavaRunner {

    Method method;
    
    Object[] args;

    public JavaRunner() {}

    public void loadMethod(String className, String methodName) {
        ClassLoader classLoader = ClassLoader.getSystemClassLoader();
        try {
            for (Method method : forName(className, true, classLoader).getMethods()){
                if (method.getName().equals(methodName)) {
                    this.method = method;
                    break;
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    public static void main(String[] args) {
        JavaRunner runner = new JavaRunner();
        while (true) {
            if (runner.method != null && runner.args != null) {
                try {
                    runner.method.invoke(null, runner.args);
                    runner.args = null;
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
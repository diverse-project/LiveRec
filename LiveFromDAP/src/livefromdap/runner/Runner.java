import java.lang.reflect.Method;
import java.net.URL;
import static java.lang.Class.forName;
import java.io.File;

public class Runner {
    private final DynamicClassLoader classLoader;
    Class clazz;
    Method method;
    Object[] args;

    public Runner() {
        classLoader = new DynamicClassLoader(new URL[0], this.getClass().getClassLoader());
    }

    public void addPath(String path) {
        try {
            File file = new File(path);
            if(file.exists()) {
                URL url = file.toURI().toURL();
                classLoader.addURL(url);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void loadClass(String className) {
        try {
            clazz = forName(className, true, classLoader);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void loadMethod(String methodName) {
        try {
            for (Method method : clazz.getMethods()){
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
        Runner runner = new Runner();
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

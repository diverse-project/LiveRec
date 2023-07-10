import java.lang.reflect.Method;
import java.net.URL;
import java.util.ArrayList;

import java.io.File;

public class Runner {
    private final DynamicClassLoaderFactory classLoaderFactory;
    Class clazz;
    Method method;
    Object[] args;

    public Runner() {
        classLoaderFactory = new DynamicClassLoaderFactory(new ArrayList<>(), this.getClass().getClassLoader());
    }

    public void addPath(String path) {
        try {
            File file = new File(path);
            if(file.exists()) {
                URL url = file.toURI().toURL();
                classLoaderFactory.addURL(url);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void loadClass(String className) {
        try {
            clazz = classLoaderFactory.loadClass(className);
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
        Object result;
        while (true) {
            if (runner.method != null && runner.args != null) {
                try {
                    result = runner.method.invoke(null, runner.args);
                    runner.args = null;
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
}

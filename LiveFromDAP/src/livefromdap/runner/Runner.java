import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
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
            if (runner.method != null) {
                try {
                    // check if static
                    if (Modifier.isStatic(runner.method.getModifiers())) {
                        result = runner.method.invoke(null, runner.args);
                    } else {
                        // find the minimal constructor for the class
                        Object classInstance;
                        if (runner.clazz.getConstructors().length == 0) {
                            // raise error
                            throw new Exception("No constructor found");
                        }
                        // get constructor, order them by parameter count
                        Constructor[] constructors = runner.clazz.getConstructors();
                        constructors = Arrays.stream(constructors).sorted(Comparator.comparing(Constructor::getParameterCount)).toArray(Constructor[]::new);
                        Constructor constructor = constructors[0];
                        if (constructor.getParameterCount() == 0) {
                            classInstance = constructor.newInstance();
                        } else {
                            // initialize the class with all parameters as null
                            Object[] constructorArgs = new Object[constructor.getParameterCount()];
                            for (int i = 0; i < constructor.getParameterCount(); i++) {
                                constructorArgs[i] = null;
                            }
                            classInstance = constructor.newInstance(constructorArgs);
                        }
                        result = runner.method.invoke(classInstance, runner.args);
                    }
                    runner.method = null;
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
}

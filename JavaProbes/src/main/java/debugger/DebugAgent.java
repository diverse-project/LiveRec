package debugger;

import java.io.File;
import java.net.URL;
import java.util.ArrayList;

import static java.lang.Class.forName;

public class DebugAgent {
    private final DynamicClassLoaderFactory classLoaderFactory;
    public DebugAgent() {
        classLoaderFactory = new DynamicClassLoaderFactory(new ArrayList<>(), this.getClass().getClassLoader());
    }

    public void addPath(String path) {
        System.out.println("Adding path: " + path);
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

    public Class loadClass(String className) {
        System.out.println("Loading class: " + className);
        try {
            Class clazz = classLoaderFactory.loadClass(className);
            forName(className, true, classLoaderFactory.getClassLoader()); // additional to force class preparation
            return clazz;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    public static void main(String[] args) {
        while (true) {}
    }
}
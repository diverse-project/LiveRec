package debugger;

import java.net.URL;
import java.util.List;

public class DynamicClassLoaderFactory {
    List<URL> urls;
    ClassLoader parent;
    DynamicClassLoader dynamicClassLoader;

    public DynamicClassLoaderFactory(List<URL> urls, ClassLoader parent) {
        this.urls = urls;
        this.parent = parent;
    }

    public void addURL(URL url) {
        urls.add(url);
    }

    public Class loadClass(String className) {
        try {
            dynamicClassLoader = new DynamicClassLoader(urls.toArray(new URL[0]), parent);
            Class loadedClass = dynamicClassLoader.loadClass(className);
            return loadedClass;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public ClassLoader getClassLoader() {
        return dynamicClassLoader;
    }
}

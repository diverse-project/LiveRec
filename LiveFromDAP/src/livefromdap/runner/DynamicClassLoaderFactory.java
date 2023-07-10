import java.net.URL;
import java.util.List;

public class DynamicClassLoaderFactory {
    List<URL> urls;
    ClassLoader parent;

    public DynamicClassLoaderFactory(List<URL> urls, ClassLoader parent) {
        this.urls = urls;
        this.parent = parent;
    }

    public void addURL(URL url) {
        urls.add(url);
    }

    public Class loadClass(String className) {
        try {
            DynamicClassLoader tempClassLoader = new DynamicClassLoader(urls.toArray(new URL[0]), parent);
            Class loadedClass = tempClassLoader.loadClass(className);
            return loadedClass;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
}

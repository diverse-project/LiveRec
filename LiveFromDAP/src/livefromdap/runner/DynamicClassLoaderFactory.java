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

    public DynamicClassLoader create() {
        return new DynamicClassLoader(urls.toArray(new URL[0]), parent);
    }

    public Class loadClass(String className) {
        try {
            return create().loadClass(className);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
}

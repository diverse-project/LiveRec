package debugger;

import java.net.URL;
import java.net.URLClassLoader;

public class DynamicClassLoader extends URLClassLoader {
    public DynamicClassLoader(URL[] urls, ClassLoader parent) {
        super(urls, parent);
    }

    @Override
    public void addURL(URL url) {
        super.addURL(url);
    }

}

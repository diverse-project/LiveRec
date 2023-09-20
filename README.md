# LiveProbes

## Structure

### `JavaProbes/`

This folder contains a Java project, tha demonstrate how to get live programming features using a debugger(here we use [JDI](https://docs.oracle.com/javase/8/docs/technotes/guides/jpda/jdwp-spec.html)).

### `LiveFromDAP/`

This folder contains a Python library that use the Debugging Adapter Protocol to get live programming features. It supports Python and C. There is also a web demo of a live interface for C.

## Docker

```bash
docker compose up -d
docker compose exec web bash
# In the shell
flask -A src/webdemo/main.py:app run
```

The liverec server is available at `http://localhost:5000/`
Currently, the web demo does not work properly with Javascript, but it works with C, Python and Java.



*Note : the `CMD` and `ENTRYPOINT` are not used because OpenDebugAD7 (C Debug Server) crash*


## Web Demo of Live Probes

### C
![](https://github.com/jbdoderlein/LiveProbes/blob/master/assets/dap_c_demo.gif)

### Java
![](https://github.com/jbdoderlein/LiveProbes/blob/master/assets/dap_java_demo.gif)

### Python
![](https://github.com/jbdoderlein/LiveProbes/blob/master/assets/dap_python_demo.gif)


package debugger;

public class ObjectInvocationRequest {

    private final String className;

    private final Object[] args;
    ObjectInvocationRequest(String className, Object... args) {
        this.className = className;
        this.args = args;
    }

    public String getClassName() {
        return className;
    }

    public Object[] getArgs() {
        return args;
    }
}

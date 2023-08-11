package debugger;

import com.sun.jdi.*;

import java.util.ArrayList;
import java.util.List;
import java.lang.reflect.Array;

/**
 * MirrorCreator
 * This class is used to create a mirror of the object in the JDI VM.
 */
public class MirrorCreator {

    private final VirtualMachine vm;

    private ObjectReference debugAgent;

    MirrorCreator(VirtualMachine vm) {
        this.vm = vm;
    }

    public void setDebugAgent(ObjectReference debugAgent) {
        this.debugAgent = debugAgent;
    }

    public List<Value> convert(Object... args) throws ClassNotLoadedException, InvalidTypeException, IncompatibleThreadStateException, InvocationException {
        List<Value> values = new ArrayList<>();
        for (Object o : args) {
            values.add(this.mirrorOf(o));
        }
        return values;
    }

    public Value mirrorOf(Object o) throws ClassNotLoadedException, InvalidTypeException, IncompatibleThreadStateException, InvocationException {
        if (o instanceof Boolean b){
            return this.mirrorOf(b);
        } else if (o instanceof Byte b) {
            return this.mirrorOf(b);
        } else if (o instanceof Character c) {
            return this.mirrorOf(c);
        } else if (o instanceof Short s) {
            return this.mirrorOf(s);
        } else if (o instanceof Integer i) {
            return this.mirrorOf(i);
        } else if (o instanceof Long l) {
            return this.mirrorOf(l);
        } else if (o instanceof Float f) {
            return this.mirrorOf(f);
        } else if (o instanceof Double d) {
            return this.mirrorOf(d);
        } else if (o instanceof String s) {
            return this.mirrorOf(s);
        } else if (o.getClass().getName().charAt(0) == '[') { // array
            int length = Array.getLength(o);
            List<Value> values = new ArrayList<>();

            for (int i = 0; i < length; i++) {
                values.add(this.mirrorOf(Array.get(o, i)));
            }
            return this.mirrorOf(values, o.getClass().getTypeName());
        } else if (o instanceof ObjectInvocationRequest a) {
            return this.mirrorOf(a);
        }
        return null;
    }

    private BooleanValue mirrorOf(Boolean b) {
        return vm.mirrorOf(b);
    }

    private ByteValue mirrorOf(Byte b) {
        return vm.mirrorOf(b);
    }

    private CharValue mirrorOf(Character c) {
        return vm.mirrorOf(c);
    }

    private ShortValue mirrorOf(Short s) {
        return vm.mirrorOf(s);
    }

    private IntegerValue mirrorOf(Integer i) {
        return vm.mirrorOf(i);
    }

    private LongValue mirrorOf(Long l) {
        return vm.mirrorOf(l);
    }

    private FloatValue mirrorOf(Float f) {
        return vm.mirrorOf(f);
    }

    private DoubleValue mirrorOf(Double d) {
        return vm.mirrorOf(d);
    }

    private StringReference mirrorOf(String s) {
        return vm.mirrorOf(s);
    }


    private ArrayReference mirrorOf(List<Value> a, String listType) throws ClassNotLoadedException, InvalidTypeException {
        ArrayType arrayDef = (ArrayType) vm.classesByName(listType).get(0);
        ArrayReference array = arrayDef.newInstance(a.size());
        array.setValues(a);
        return array;
    }

    public void addClassPath(String path) throws ClassNotLoadedException, InvalidTypeException, IncompatibleThreadStateException, InvocationException {
        debugAgent.invokeMethod(vm.allThreads().get(0), debugAgent.referenceType().methodsByName("addPath").get(0), convert(path), ObjectReference.INVOKE_SINGLE_THREADED);
    }

    public ClassType loadClass(String className) throws ClassNotLoadedException, InvalidTypeException, IncompatibleThreadStateException, InvocationException {
        ClassObjectReference classLoaded = (ClassObjectReference) debugAgent.invokeMethod(vm.allThreads().get(0), debugAgent.referenceType().methodsByName("loadClass").get(0), convert(className), ObjectReference.INVOKE_SINGLE_THREADED);
        if (classLoaded == null) {
            throw new ClassNotLoadedException(className);
        }
        return (ClassType) classLoaded.reflectedType();
    }

    public ClassType getClassType(String className){
        List<ReferenceType> classes = vm.classesByName(className);
        if (classes.isEmpty()) {
            try{
                return loadClass(className);
            } catch (Exception e){
                e.printStackTrace();
            }
        }
        // get the last class loaded
        return (ClassType) classes.get(0);
    }

    public Method getMethod(String className, String debugMethod){
        ClassType classType = getClassType(className);
        return classType.methodsByName(debugMethod).get(0);
    }

    private ObjectReference mirrorOf(ObjectInvocationRequest objectInvocationRequest) throws ClassNotLoadedException, InvalidTypeException, IncompatibleThreadStateException, InvocationException {
        List<ReferenceType> classes = vm.classesByName(objectInvocationRequest.getClassName());
        if (classes.isEmpty()) {
            loadClass(objectInvocationRequest.getClassName());
            classes = vm.classesByName(objectInvocationRequest.getClassName());
        }
        ClassType objectClassType = (ClassType) classes.get(0);

        List<Method> methods = objectClassType.methodsByName("<init>");
        Method constructor = methods.get(0);
        return objectClassType.newInstance(vm.allThreads().get(0), constructor, convert(objectInvocationRequest.getArgs()), ObjectReference.INVOKE_SINGLE_THREADED);
    }
}

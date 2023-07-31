package debugger;

import java.io.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicReference;

import com.sun.jdi.*;
import com.sun.jdi.connect.Connector;
import com.sun.jdi.connect.IllegalConnectorArgumentsException;
import com.sun.jdi.connect.LaunchingConnector;
import com.sun.jdi.connect.VMStartException;
import com.sun.jdi.event.*;
import com.sun.jdi.request.*;


enum State {
    BOOTING,
    READY,
    RUNNING,
    DEAD,
    TERMINATED,
}


public class Debugger {
    private static final String DEBUG_CLASS_PATH = "target/classes";
    private static final String DEBUG_CLASS = "debugger.DebugAgent";
    private String currentClassPath;
    private String currentClass;
    private String currentMethod;
    private final long autoRestart;

    private final AtomicReference<VirtualMachine> vm;

    private final AtomicReference<StackRecording> currentStackRecording = new AtomicReference<>();

    private Thread eventHandler;

    private final Object stateLock = new Object();
    private final AtomicReference<State> state;

    private final AtomicReference<MirrorCreator> mirrorCreator;
    private final AtomicReference<ObjectReference> agentObjectReference;

    private final AtomicReference<ObjectReference> debugObjectReference;


    public State getState() {
        return state.get();
    }

    public void setState(State newState) {
        state.set(newState);
        synchronized (stateLock) {
            stateLock.notifyAll();
        }
    }

    public StackRecording getCurrentStackRecording() {
        return currentStackRecording.get();
    }

    public void addVariableMap(int lineNumber, HashMap<String, String> variableMap) {
        if (currentStackRecording.get() == null) {
            currentStackRecording.set(new StackRecording());
        }
        currentStackRecording.get().addStackFrame(new StackFrame(lineNumber, variableMap));
    }

    Debugger(long autoRestart) {
        this.autoRestart = autoRestart;
        this.vm = new AtomicReference<>();
        this.state = new AtomicReference<>(State.BOOTING);
        this.agentObjectReference = new AtomicReference<>();
        this.debugObjectReference = new AtomicReference<>();
        this.mirrorCreator = new AtomicReference<>();
    }

    Debugger() {
        this(0);
    }

    public void loadClass(String classPath, String className) throws ClassNotLoadedException, InvalidTypeException, IncompatibleThreadStateException, InvocationException {
        assertVMReady();
        initializeContexts();
        if (this.currentClassPath == null || !this.currentClassPath.equals(classPath)) {
            mirrorCreator.get().addClassPath(classPath);
        }
        currentClassPath = classPath;
        if (this.currentClass == null || vm.get().classesByName(className).isEmpty()) {
            EventRequestManager mgr = vm.get().eventRequestManager();
            ClassPrepareRequest classPrepareRequest = mgr.createClassPrepareRequest();
            classPrepareRequest.addClassFilter(className);
            classPrepareRequest.enable();
        }
        currentClass = className; // Will be auto loaded when needed
        //setState(State.RUNNING);
    }


    public void connectAndLaunchVM() throws IOException, IllegalConnectorArgumentsException, VMStartException {
        LaunchingConnector launchingConnector = Bootstrap.virtualMachineManager().defaultConnector();
        Map<String, Connector.Argument> arguments = launchingConnector.defaultArguments();
        arguments.get("main").setValue("-classpath "+ DEBUG_CLASS_PATH + " " + DEBUG_CLASS);
        vm.set(launchingConnector.launch(arguments));
        mirrorCreator.set(new MirrorCreator(vm.get()));
    }

    public void enableClassPrepareRequest() {
        EventRequestManager mgr = vm.get().eventRequestManager();

        //Create a special class prepare requests for debugger.DebugAgent
        ClassPrepareRequest debugAgentRequest = mgr.createClassPrepareRequest();
        debugAgentRequest.addClassFilter(DEBUG_CLASS);
        debugAgentRequest.enable();
    }


    private void initializeContexts() throws ClassNotLoadedException, IncompatibleThreadStateException, InvocationException, InvalidTypeException {
        // If no agent context, create one
        if (agentObjectReference.get() == null) {
            ObjectInvocationRequest objectInvocationRequest = new ObjectInvocationRequest(DEBUG_CLASS);
            agentObjectReference.set((ObjectReference) mirrorCreator.get().mirrorOf(objectInvocationRequest));
            mirrorCreator.get().setDebugAgent(agentObjectReference.get());
        }

        // If no debug method context, create one
        if (debugObjectReference.get() == null && currentClass != null) {
            ObjectInvocationRequest objectInvocationRequest = new ObjectInvocationRequest(currentClass);
            debugObjectReference.set((ObjectReference) mirrorCreator.get().mirrorOf(objectInvocationRequest));
        }
    }

    private Optional<Value> callFunction(Object... arguments) throws InterruptedException, IllegalConnectorArgumentsException, VMStartException, IOException, ClassNotLoadedException, InvalidTypeException, IncompatibleThreadStateException, InvocationException {
        assertVMReady();
        // New StackFrame saver
        currentStackRecording.set(new StackRecording());

        // Initialize contexts
        initializeContexts();
        // filter by name contain a


        // Start the function
        CompletableFuture<Boolean> invokeSuccess = new CompletableFuture<>();
        CompletableFuture<Value> returnValue = new CompletableFuture<>();
        setState(State.RUNNING);
        Thread thread1 = new Thread(() -> {
            try {
                List<Value> argumentValues = mirrorCreator.get().convert(arguments);
                Value returnedValue = debugObjectReference.get().invokeMethod(getThread(), mirrorCreator.get().getMethod(currentClass, currentMethod), argumentValues, ObjectReference.INVOKE_SINGLE_THREADED);
                invokeSuccess.complete(true);
                returnValue.complete(returnedValue);
            }
            catch (Exception e) {
                invokeSuccess.complete(false);
            }
        });
        thread1.start();
        // Get with timeout
        try {
            thread1.join(autoRestart);
            Boolean success = invokeSuccess.get(autoRestart, TimeUnit.MILLISECONDS);
            if (Boolean.TRUE.equals(success)) {
                Value returnedValue = returnValue.get(autoRestart, TimeUnit.MILLISECONDS);
                setState(State.READY);
                return Optional.of(returnedValue);
            }
            else {
                setState(State.DEAD);
                restart();
            }
        }
        catch (InterruptedException e){
            throw e;
        }
        catch (TimeoutException e) {
            setState(State.DEAD);
            restart();
        }
        catch (Exception e) {
            e.printStackTrace();
        }
        return Optional.empty();
    }

    public Value execute(String method, Object... arguments) {
        Value value = null;
        currentMethod = method;
        while (value == null) {
            // if not the same vm from context, then we need to restart the vm
            try {
                value = callFunction(arguments).orElse(null);
            }
            catch (InterruptedException e) {
                e.printStackTrace();
                Thread.currentThread().interrupt();
            }
            catch (Exception e) {
                e.printStackTrace();
            }
        }
        return value;
    }

    public void reloadClass(String className) throws ClassNotLoadedException, IncompatibleThreadStateException, InvocationException, InvalidTypeException {
        assertVMReady();
        // Initialize contexts
        initializeContexts();
        mirrorCreator.get().loadClass(className);
    }

    public void probeVariables(LocatableEvent event)  throws AbsentInformationException {
        com.sun.jdi.StackFrame stackFrame;
        try {
            stackFrame = event.thread().frame(0);
        }
        catch (Exception e) {
            return;
        }
        if(stackFrame.location().toString().contains(currentClass) && stackFrame.location().method().name().equals(currentMethod)) {
            Map<LocalVariable, Value> visibleVariables = stackFrame.getValues(stackFrame.visibleVariables());
            HashMap<String, String> visibleResolvedVariables = new HashMap<>();
            for (Map.Entry<LocalVariable, Value> entry : visibleVariables.entrySet()) {
                if (entry.getValue() instanceof ArrayReference arrayReference){
                    visibleResolvedVariables.put(entry.getKey().name(), arrayReference.getValues().toString());
                }
                else {
                    visibleResolvedVariables.put(entry.getKey().name(), entry.getValue().toString());
                }
            }
            addVariableMap(event.location().lineNumber(), visibleResolvedVariables);
        }
    }

    public void addMethodCallStackFrame(LocatableEvent event) throws IncompatibleThreadStateException, AbsentInformationException {
        com.sun.jdi.StackFrame stackFrame = event.thread().frame(0);
        List<Value> argsValues = stackFrame.getArgumentValues();
        Method method = stackFrame.location().method();
        HashMap<String, String> args = new HashMap<>();
        List<String> argNames = method.arguments().stream().map(LocalVariable::name).toList();
        for (int i = 0; i < argsValues.size(); i++) {
            if (argsValues.get(i) instanceof ArrayReference arrayReference){
                args.put(argNames.get(i), arrayReference.getValues().toString());
            }
            else {
                args.put(argNames.get(i), argsValues.get(i).toString());
            }
        }
        addVariableMap(-1, args);
    }

    private void assertVMReady() {
        synchronized (stateLock){
            while (getState() != State.READY) {
                try {
                    stateLock.wait();
                }
                catch (InterruptedException ignored) {
                    Thread.currentThread().interrupt();
                }
            }
        }
    }

    private ThreadReference getThread() {
        return vm.get().allThreads().get(0);
    }

    public void start() throws IllegalConnectorArgumentsException, VMStartException, IOException {
        connectAndLaunchVM();
        enableClassPrepareRequest();
        Runnable invokeRunnable = () -> {
            try {
                EventSet eventSet;
                while ((eventSet = vm.get().eventQueue().remove()) != null) {
                    // print status of the vm
                    int doIResume = 0;
                    for (Event event : eventSet) {
                        // print event
                        if(handleEvent(event)){
                            doIResume++;
                        }
                        // get state of the thread
                    }
                    for (int i = 0; i < doIResume; i++) {
                        getThread().resume();
                    }
                }
            } catch (Exception e) {
                setState(State.TERMINATED);
                Thread.currentThread().interrupt();
            }
        };
        eventHandler = new Thread(invokeRunnable);
        eventHandler.start();
    }

    public void stop() throws InterruptedException {
        vm.get().exit(0);
        eventHandler.join();
        setState(State.DEAD);
    }

    public void restart() throws IllegalConnectorArgumentsException, VMStartException, IOException, InterruptedException {
        stop();
        currentStackRecording.set(null);
        vm.set(null);
        agentObjectReference.set(null);
        debugObjectReference.set(null);
        mirrorCreator.set(null);
        state.set(State.BOOTING);
        start();
    }

    /*
    * Event handlers
    * All the code below is used in the event handler
    * Do not call any method invocation here, deadlocks will happen
     */

    private boolean handleEvent(Event event) throws IncompatibleThreadStateException, AbsentInformationException {
        // Print the vm main thread state
        if (event instanceof StepEvent stepEvent) {
            this.probeVariables(stepEvent);
        } else if (event instanceof ClassPrepareEvent classPrepareEvent) {
            return handleClassPrepareEvent(classPrepareEvent);
        } else if (event instanceof BreakpointEvent breakpointEvent) {
            return handleBreakpointEvent(breakpointEvent);
        } else if (event instanceof MethodEntryEvent methodEntryEvent) {
           return handleMethodEntryEvent(methodEntryEvent);
        } else if (event instanceof MethodExitEvent methodExitEvent) {
            return handleMethodExitEvent(methodExitEvent);
        }
        return true;
    }

    private boolean handleClassPrepareEvent(ClassPrepareEvent event) throws AbsentInformationException{
        ClassType classType = (ClassType) event.referenceType();
        EventRequestManager mgr = vm.get().eventRequestManager();
        if (Objects.equals(classType.name(), DEBUG_CLASS)) {
            Method method = classType.methodsByName("main").get(0);
            Location location = method.allLineLocations().get(0);
            BreakpointRequest breakpointRequest = mgr.createBreakpointRequest(location);
            breakpointRequest.setSuspendPolicy(EventRequest.SUSPEND_ALL);
            breakpointRequest.enable();
        }
        if (Objects.equals(classType.name(), currentClass) || Objects.equals(classType.name(), DEBUG_CLASS)){
            MethodEntryRequest entryRequest = mgr.createMethodEntryRequest();
            MethodExitRequest exitRequest = mgr.createMethodExitRequest();

            entryRequest.addClassFilter(classType);
            exitRequest.addClassFilter(classType);

            entryRequest.setSuspendPolicy(EventRequest.SUSPEND_ALL);
            exitRequest.setSuspendPolicy(EventRequest.SUSPEND_ALL);

            entryRequest.enable();
            exitRequest.enable();
        }
        return true;
    }

    private boolean handleBreakpointEvent(BreakpointEvent breakpointEvent) throws IncompatibleThreadStateException, AbsentInformationException {
        if (Objects.equals(breakpointEvent.location().declaringType().name(), DEBUG_CLASS)){
            setState(State.READY);
            return false;
        }
        return true;
    }

    private boolean handleMethodEntryEvent(MethodEntryEvent methodEntryEvent) throws IncompatibleThreadStateException, AbsentInformationException {
        // print the current stack frame variables
        EventRequestManager mgr = vm.get().eventRequestManager();
        if (Objects.equals(methodEntryEvent.location().declaringType().name(), currentClass) && Objects.equals(methodEntryEvent.location().method().name(), currentMethod)) {
            addMethodCallStackFrame(methodEntryEvent);
            probeVariables(methodEntryEvent);
            if (!mgr.stepRequests().isEmpty()) {
                if (!mgr.stepRequests().get(0).isEnabled()) {
                    mgr.stepRequests().get(0).enable();
                }
            }
            else {
                StepRequest request = mgr.createStepRequest(methodEntryEvent.thread(), StepRequest.STEP_LINE, StepRequest.STEP_OVER);
                request.enable();
            }
        } else if (Objects.equals(methodEntryEvent.location().declaringType().name(), DEBUG_CLASS) && Objects.equals(methodEntryEvent.location().method().name(), "main") && (!mgr.stepRequests().isEmpty() && (mgr.stepRequests().get(0).isEnabled()))) {
            mgr.stepRequests().get(0).disable();
        }
        return true;
    }

    private boolean handleMethodExitEvent(MethodExitEvent methodExitEvent){
        if (Objects.equals(methodExitEvent.location().declaringType().name(), currentClass) && Objects.equals(methodExitEvent.location().method().name(), currentMethod)) {
            EventRequestManager mgr = vm.get().eventRequestManager();
            if (!mgr.stepRequests().isEmpty() && (mgr.stepRequests().get(0).isEnabled())) {
                mgr.stepRequests().get(0).disable();
            }
        }
        return true;
    }


}

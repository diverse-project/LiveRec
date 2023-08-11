package debugger;

// import json
import com.sun.jdi.*;
import com.sun.jdi.connect.IllegalConnectorArgumentsException;
import com.sun.jdi.connect.VMStartException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.Scanner;

public class LiveAgent {
    /* Live agent class interact as CLI for Debugger, to be used in LiveFromDAP webdemo
     * It receive json as single line and output json also
     */
    Debugger debugger;

    public LiveAgent() throws IllegalConnectorArgumentsException, VMStartException, IOException {
        debugger = new Debugger(0);
        debugger.start();
        JSONObject result = new JSONObject();
        result.put("status", "ready");
        //get the current path where this is launched
        result.put("path", System.getProperty("user.dir"));
        System.out.println(result.toString());
    }

    private String process(String line) throws ClassNotLoadedException, IncompatibleThreadStateException, InvocationException, InvalidTypeException {
        //parse json
        JSONObject json = new JSONObject(line);
        String command = json.getString("command");
        JSONObject params = json.getJSONObject("params");
        JSONObject result = new JSONObject();
        if (command.equals("loadClass")) {
            try{
                debugger.loadClass(params.getString("path"), params.getString("className"));
                result.put("status", "ok");
            } catch (Exception e) {
                result.put("status", "error");
                result.put("message", e.getMessage());
            }
        } else if (command.equals("evaluate")){
            String methodName = params.getString("method");
            String[] argsString = params.getJSONArray("args").toList().toArray(new String[0]);
            Object[] args = new Object[argsString.length];
            // we need to convert the args that are string to the actual object
            // to do this we need to parseInt, parseDouble, etc
            for (int i = 0; i < argsString.length; i++) {
                String arg = argsString[i];
                if (arg.equals("true") || arg.equals("false")) {
                    args[i] = Boolean.parseBoolean(arg);
                } else if (arg.contains(".")) {
                    args[i] = Double.parseDouble(arg);
                } else {
                    args[i] = Integer.parseInt(arg);
                }
            }
            // execute, need to unpack the args as arguments
            // so for example if args = [1, 2, 3], we need to call execute(method_name, 1, 2, 3)
            Value resultObject = debugger.execute(methodName, args);
            StackRecording recording = debugger.getCurrentStackRecording();
            result.put("status", "ok");
            result.put("result", resultObject.toString());
            result.put("stack", recording.toJSON());
        } else {
            result.put("status", "error");
            result.put("message", "unknown command");
        }
        return result.toString();
    }

    public void run() throws ClassNotLoadedException, IncompatibleThreadStateException, InvocationException, InvalidTypeException {
        while (true) {
            // use scanner to read from stdin
            Scanner scanner = new Scanner(System.in);
            String line = scanner.nextLine();
            String result = process(line);
            System.out.println(result);
        }
    }

    public static void main(String[] args) throws IllegalConnectorArgumentsException, VMStartException, IOException, ClassNotLoadedException, IncompatibleThreadStateException, InvocationException, InvalidTypeException {
        LiveAgent agent = new LiveAgent();
        agent.run();
    }
}

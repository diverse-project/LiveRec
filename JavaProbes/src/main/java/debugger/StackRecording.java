package debugger;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.LinkedList;
import java.util.List;

public class StackRecording{
    List<StackFrame> stackFrames = new LinkedList<>();

    //length of stack recording
    public int length(){
        return stackFrames.size();
    }

    public StackRecording(){
        super();
    }

    public void addStackFrame(StackFrame stackFrame){
        // add the last stack frame as predecessor
        if(!stackFrames.isEmpty()){
            stackFrame.setPredecessor(stackFrames.get(stackFrames.size() - 1));
            stackFrames.get(stackFrames.size() - 1).setSuccessor(stackFrame);
        }
        stackFrames.add(stackFrame);
    }

    public List<StackFrame> getStackFrames(){
        return stackFrames;
    }

    public StackFrame getStackFrame(int index){
        return stackFrames.get(index);
    }

    public JSONArray toJSON(){
        JSONArray json = new JSONArray();
        for (int i = 0; i < stackFrames.size(); i++) {
            json.put(stackFrames.get(i).toJSON());
        }
        return json;
    }

    public void clear() {
        stackFrames.clear();
    }
}

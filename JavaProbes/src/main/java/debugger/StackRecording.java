package debugger;

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
}

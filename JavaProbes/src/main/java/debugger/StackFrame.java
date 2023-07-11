package debugger;

import java.util.HashMap;

public class StackFrame {

    private final Integer lineNumber;

    private final HashMap<String, String> map;
    private StackFrame predecessor = null;
    private StackFrame successor = null;
    public StackFrame(Integer lineNumber, HashMap<String, String> map) {
        this.lineNumber = lineNumber;
        this.map = map;
    }

    public void setPredecessor(StackFrame predecessor) {
        this.predecessor = predecessor;
    }

    public void setSuccessor(StackFrame successor) {
        this.successor = successor;
    }

    public StackFrame getPredecessor() {
        return predecessor;
    }

    public StackFrame getSuccessor() {
        return successor;
    }

    public HashMap<String, String> getMap() {
        return map;
    }

    public Integer getLineNumber() {
        return lineNumber;
    }

    public String getVariable(String name) {
        return map.get(name);
    }

}

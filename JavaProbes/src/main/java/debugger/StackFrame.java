package debugger;

import org.json.JSONArray;
import org.json.JSONObject;

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

    public JSONObject toJSON() {
        // Respect the same format of LiveFromDAP
        JSONObject json = new JSONObject();
        JSONObject position = new JSONObject();
        position.put("line", lineNumber);
        position.put("column", 0);
        json.put("pos", position);
        json.put("height", 1);
        json.put("lineNumber", lineNumber);
        JSONArray variables = new JSONArray();
        for (String key : this.map.keySet()) {
            JSONObject variable = new JSONObject();
            variable.put("name", key);
            variable.put("value", this.map.get(key));
            variables.put(variable);
        }
        json.put("variables", variables);
        json.put("id", this.hashCode());
        json.put("predecessor", this.predecessor == null ? -1 : this.predecessor.hashCode());
        json.put("successor", this.successor == null ? -1 : this.successor.hashCode());
        return json;
    }

}

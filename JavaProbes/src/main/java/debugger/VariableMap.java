package debugger;

import org.json.JSONArray;
import org.json.JSONObject;

import org.javatuples.Pair;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.TreeMap;

public class VariableMap {

    private final TreeMap<Integer, List<HashMap<String, String>>> diffMap = new TreeMap<>();
    public final TreeMap<Integer, List<HashMap<String, String>>> valueMap = new TreeMap<>();

    private final List<Pair<Integer,HashMap<String, String>>> stackFrameHistory = new ArrayList<>();
    private Integer lastLine = null;
    private HashMap<String, String> lastValue = null;

    public VariableMap() {
        super();
    }

    public void addStackFrame(Integer lineNumber, HashMap<String, String> map) {
        // History of stack frames in order of execution
        stackFrameHistory.add(new Pair<>(lineNumber, map));

        // Values over time
        if (!valueMap.containsKey(lineNumber)) {
            valueMap.put(lineNumber, new ArrayList<>());
        }
        valueMap.get(lineNumber).add(map);

        // Diff between values
        if (lineNumber == -1) {
            diffMap.put(lineNumber, new ArrayList<>());
            diffMap.get(lineNumber).add(map);
        }
        else{
            if (lastValue != null || lastLine != null) {
                // We need to see difference between the last value and the current value
                HashMap<String, String> diff = getDiff(lastValue, map);
                if (diff.size() > 0) {
                    // There is a difference, so we need to add it to the list
                    diffMap.computeIfAbsent(lastLine, k -> new ArrayList<>());
                    diffMap.get(lastLine).add(diff);
                }
            }
            lastValue = map;
            lastLine = lineNumber;
        }
    }


    private HashMap<String, String> getDiff(HashMap<String, String> previous, HashMap<String, String> current) {
        HashMap<String, String> diff = new HashMap<>();
        for (String key : current.keySet()) {
            if (!previous.containsKey(key) || !previous.get(key).equals(current.get(key))) {
                diff.put(key, current.get(key));
            }
        }
        return diff;
    }


    public JSONObject valueToJSON() {
        // Convert the treemap to a dictionary, the list to a list, and the hashmap to a dictionary
        // Then convert the dictionary to a JSON string
        JSONObject json = new JSONObject();
        for (Integer key : valueMap.keySet()) {
            List<HashMap<String, String>> list = valueMap.get(key);
            JSONArray jsonList = new JSONArray();
            for (HashMap<String, String> map : list) {
                JSONObject mapJSON = new JSONObject();
                for (String mapKey : map.keySet()) {
                    mapJSON.put(mapKey, map.get(mapKey));
                }
                jsonList.put(mapJSON);
            }
            json.put(key.toString(), jsonList);
        }
        return json;
    }

    public JSONObject diffToJSON() {
        // Convert the treemap to a dictionary, the list to a list, and the hashmap to a dictionary
        // Then convert the dictionary to a JSON string
        JSONObject json = new JSONObject();
        for (Integer key : diffMap.keySet()) {
            List<HashMap<String, String>> list = diffMap.get(key);
            JSONArray jsonList = new JSONArray();
            for (HashMap<String, String> map : list) {
                JSONObject mapJSON = new JSONObject();
                for (String mapKey : map.keySet()) {
                    mapJSON.put(mapKey, map.get(mapKey));
                }
                jsonList.put(mapJSON);
            }
            json.put(key.toString(), jsonList);
        }
        return json;
    }

    public List<String> extractVariable(String variableName, List<HashMap<String, String>> list) {
        List<String> values = new ArrayList<>();
        for (HashMap<String, String> map : list) {
            if (map.containsKey(variableName)) {
                values.add(map.get(variableName));
            }
        }
        return values;
    }

}

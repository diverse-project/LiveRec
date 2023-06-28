package debugger;

import com.sun.jdi.Value;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

public class PrettyPrinterTest {

    @Test
    void testPrettyPrinter() throws Exception {
        Debugger debuggerInstance = new Debugger("target/classes", "samples.BretVictorExample", "binarySearch", 200);
        debuggerInstance.start();
        char[] array = new char[]{'a', 'b', 'c', 'd', 'e', 'f'};
        List<Character> list = new ArrayList<>();
        for (char c : array) {
            list.add(c);
        }
        char key = 'g';
        // wait for the vm to be finished
        Value v = debuggerInstance.callFunctionUntilValue(array, key);
        // Check that if key is in array, then the result is the index of key in array

        PrettyPrinter prettyPrinter = new PrettyPrinter("src/main/java/", "samples.BretVictorExample", "binarySearch");
        System.out.println(debuggerInstance.getCurrentVariableMap().valueToJSON());
        System.out.println(debuggerInstance.getCurrentVariableMap().diffToJSON());

        String output = prettyPrinter.getResult(debuggerInstance.getCurrentVariableMap());
        System.out.println(output);
        debuggerInstance.stop();
    }
}

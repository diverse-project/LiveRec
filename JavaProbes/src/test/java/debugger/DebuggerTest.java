package debugger;

import com.sun.jdi.Value;
import com.sun.jdi.VoidValue;
import org.junit.jupiter.api.Test;

import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class DebuggerTest {
    @Test
    void testBretVictorExample() throws Exception {
        Debugger debuggerInstance = new Debugger(200);
        debuggerInstance.start();
        debuggerInstance.loadClass("target/classes", "samples.BretVictorExample");
        char[] array = new char[]{'a', 'b', 'c', 'd', 'e', 'f'};
        List<Character> list = new ArrayList<>();
        for (char c : array) {
            list.add(c);
        }
        for(char key = 'a'; key < 'k'; key++) {
            // wait for the vm to be finished
            Value v = debuggerInstance.execute("binarySearch", array, key);
            // Check that if key is in array, then the result is the index of key in array
            if (list.contains(key)) {
                assertNotEquals("-1", v.toString());
            } else {
                assertEquals("-1", v.toString());
            }
            // get length of the stack recording, and assert > 0
            assertTrue(debuggerInstance.getCurrentStackRecording().length() > 0);
        }
        debuggerInstance.stop();
    }


    @Test
    void testForLoopExample() throws Exception {
        Debugger debuggerInstance = new Debugger(200);
        debuggerInstance.start();
        debuggerInstance.loadClass("target/classes", "samples.ForLoopExample");
        for(int key = 0; key < 10; key++) {
            // wait for the vm to be finished
            Value v = debuggerInstance.execute("fibonacci", key);
            // Check if the return value is not null and >= 0
            assertNotEquals("null", v.toString());
            assertNotEquals("-1", v.toString());
        }
        debuggerInstance.stop();
    }

    @Test
    void testClassReload() throws Exception {
        Debugger debuggerInstance = new Debugger(200);
        debuggerInstance.start();

        // create a new class in target/classes named UselessClass with a uselessMethod that returns 1
        String uselessClass1 = "\n" +
                "public class ChangeClass {\n" +
                "    public ChangeClass() {\n" +
                "    }\n" +
                "    public static int uselessMethod() {\n" +
                "        return 1;\n" +
                "    }\n" +
                "}\n";
        String uselessClass2 = "\n" +
                "public class ChangeClass {\n" +
                "    public ChangeClass() {\n" +
                "    }\n" +
                "    public static int uselessMethod() {\n" +
                "        return 2;\n" +
                "    }\n" +
                "}\n";
        // save uselessClass1 to src/main/java/samples/ChangeClass.java
        String path = "tmp/ChangeClass.java";
        File file = new File(path);
        FileWriter fr = new FileWriter(file);
        fr.write(uselessClass1);
        fr.close();

        // compile uselessClass1 and load it into the debugger
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        compiler.run(null, null, null, "-d", "tmp", "tmp/ChangeClass.java");
        debuggerInstance.loadClass("tmp", "ChangeClass");

        Value v = debuggerInstance.execute("uselessMethod");
        assertEquals("1", v.toString());

        // save uselessClass2 to src/main/java/samples/ChangeClass.java
        file = new File(path);
        fr = new FileWriter(file);
        fr.write(uselessClass2);
        fr.close();
        compiler.run(null, null, null, "-d", "tmp", "tmp/ChangeClass.java");
        debuggerInstance.loadClass("tmp", "ChangeClass");

        v = debuggerInstance.execute("uselessMethod");
        assertEquals("2", v.toString());

        debuggerInstance.stop();

    }


    @Test
    void testComplexObject1() throws Exception {
        Debugger debuggerInstance = new Debugger(200);
        debuggerInstance.start();
        debuggerInstance.loadClass("target/classes", "samples.ComplexObject1");
        boolean a= true;
        byte b = 1;
        char c = 'a';
        short d = 2;
        int e = 3;
        long f = 4;
        float g = 5;
        double h = 6;
        String i = "abc";
        int[] j = new int[]{1,2,3};
        Value v = debuggerInstance.execute("complexObject1", a, b, c, d, e, f, g, h, i, j);
        // Check that if key is in array, then the result is the index of key in array
        assertEquals("3", v.toString());
        debuggerInstance.stop();
    }

    @Test
    void testMultipleClassInvocation() throws Exception {
        Debugger debuggerInstance = new Debugger(200);
        debuggerInstance.start();
        debuggerInstance.loadClass("target/classes", "samples.MultipleClassInvocation");
        Value v = debuggerInstance.execute("multipleClassInvocation");
        // Check that if key is in array, then the result is the index of key in array
        assertTrue(v instanceof VoidValue);
        debuggerInstance.stop();
    }

    @Test
    void testObjectArgument() throws Exception {
        Debugger debuggerInstance = new Debugger(200);
        debuggerInstance.start();
        debuggerInstance.loadClass("target/classes", "samples.ObjectArgument");
        ObjectInvocationRequest bretVictorExampleInvocationRequest = new ObjectInvocationRequest("samples.BretVictorExample");
        ObjectInvocationRequest forLoopExampleInvocationRequest = new ObjectInvocationRequest("samples.ForLoopExample");
        Value v = debuggerInstance.execute("objectArgument", bretVictorExampleInvocationRequest, forLoopExampleInvocationRequest);
        // Check that if key is in array, then the result is the index of key in array
        assertTrue(v instanceof VoidValue);
        debuggerInstance.stop();
    }

    @Test
    void testPerformance() throws Exception {
        Debugger debuggerInstance = new Debugger(200);
        debuggerInstance.start();
        debuggerInstance.loadClass("target/classes", "samples.UselessClass");
        debuggerInstance.execute("uselessMethod", 10); //warmup

        StringBuilder sb = new StringBuilder();
        sb.append(",step, time\n");
        for(int key = 1; key < 55; key++) {
            System.out.println("Step " + key);
            long t1 = System.nanoTime();
            Value v = debuggerInstance.execute("uselessMethod", key);
            long t2 = System.nanoTime();
            StackRecording res = debuggerInstance.getCurrentStackRecording();
            sb.append(key).append(",").append(res.length()).append(",").append((t2 - t1) / 1000000000.0).append("\n");
        }
        // save to csv
        System.out.println(sb);
        debuggerInstance.stop();
    }

}

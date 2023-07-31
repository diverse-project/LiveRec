package debugger;

import com.sun.jdi.Value;
import com.sun.jdi.VoidValue;
import org.apache.bcel.classfile.ClassParser;
import org.apache.bcel.classfile.JavaClass;
import org.apache.bcel.classfile.Method;
import org.apache.bcel.generic.ICONST;
import org.apache.bcel.generic.InstructionList;
import org.junit.jupiter.api.Test;

import java.io.FileInputStream;
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
    /*
    @Test
    void testClassReload() throws Exception {
        //We need to measure the time of the execution of the function
        //get current time
        long t1 = System.nanoTime();
        Debugger debuggerInstance = new Debugger("target/classes", "samples.BretVictorExample", "binarySearch", 0);
        debuggerInstance.start();
        long t2 = System.nanoTime();
        // First we execute the function with the original class
        char key = 'a';
        char[] array = new char[]{'a', 'b', 'c', 'd', 'e', 'f'};
        Value v = debuggerInstance.callFunctionUntilValue(array, key);
        long t3 = System.nanoTime();
        // Now, get the class bytecode, modify it and reload it
        // Open with bcel the target file
        InputStream is = new FileInputStream("target/classes/samples/BretVictorExample.class");
        ClassParser parser = new ClassParser(is, "samples/BretVictorExample.class");

        JavaClass javaClass = parser.parse();
        // Modify the bytecode of the binarySearch function
        Method method = javaClass.getMethods()[1];
        InstructionList instructionList = new InstructionList(method.getCode().getCode());
        // Check that the first instruction is iconst_0
        assertEquals("iconst_0[3](1)", instructionList.getStart().getInstruction().toString());
        // change it to iconst_1
        instructionList.getStart().setInstruction(new ICONST(1));
        // Check that the first instruction is iconst_1
        assertEquals("iconst_1[4](1)", instructionList.getStart().getInstruction().toString());
        // Set the new bytecode
        method.getCode().setCode(instructionList.getByteCode());
        // Reload the class
        long t4 = System.nanoTime();
        debuggerInstance.reloadClass(javaClass.getBytes());
        long t5 = System.nanoTime();

        // Now we execute the function with the modified class
        Value v2 = debuggerInstance.callFunctionUntilValue(array, key);
        long t6 = System.nanoTime();
        // Check that the result is not the same
        assertNotEquals(v.toString(), v2.toString());

        debuggerInstance.stop();
        // Print the time in seconds
        System.out.println("Time to start the debugger: " + (t2 - t1)/1000000000.0);
        System.out.println("Time to execute the function with the original class: " + (t3 - t2)/1000000000.0);
        System.out.println("Time to reload the class: " + (t5 - t4)/1000000000.0);
        System.out.println("Time to execute the function with the modified class: " + (t6 - t5)/1000000000.0);
    }
    */

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

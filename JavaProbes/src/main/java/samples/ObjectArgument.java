package samples;

public class ObjectArgument {

    public void objectArgument(BretVictorExample bretVictorExample, ForLoopExample forLoopExample) throws InterruptedException {
        char[] array = new char[]{'a', 'b', 'c', 'd', 'e', 'f'};
        char key = 'a';
        bretVictorExample.binarySearch(array, key);
        forLoopExample.fibonacci(10);
    }
}

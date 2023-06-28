package samples;

public class MultipleClassInvocation {

    public void multipleClassInvocation() throws InterruptedException {
        BretVictorExample bretVictorExample = new BretVictorExample();
        ForLoopExample forLoopExample = new ForLoopExample();

        char[] array = new char[]{'a', 'b', 'c', 'd', 'e', 'f'};
        char key = 'a';
        bretVictorExample.binarySearch(array, key);
        forLoopExample.fibonacci(8);
    }

    public static void main(String[] args) throws InterruptedException {
        MultipleClassInvocation multipleClassInvocation = new MultipleClassInvocation();
        multipleClassInvocation.multipleClassInvocation();
    }
}

package prettyprinter;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import debugger.StackFrame;
import debugger.StackRecording;
import debugger.VariableMap;


import java.util.List;


public class SourceCodeAnnotator {

    private final StackRecording stackRecording;

    private String sourceCode;

    private final String className;

    private final String methodName;

    SourceCodeAnnotator(StackRecording stackRecording, String sourceCode, String className, String methodName) {
        this.stackRecording = stackRecording;
        CompilationUnit compilationUnit = StaticJavaParser.parse(sourceCode);
        this.sourceCode = sourceCode;
        this.className = className;
        this.methodName = methodName;
        SourceCodeVisitor sourceCodeVisitor = new SourceCodeVisitor();
        sourceCodeVisitor.visit(compilationUnit, this);
    }


    public String getClassName() {
        return className;
    }


    public String getMethodName() {
        return methodName;
    }


    public String getSourceCode() {
        return sourceCode;
    }


    public String getVariable(String variableName, Integer lineNumber) {
        StringBuilder stringBuilder = new StringBuilder();
        for (StackFrame stackFrame : stackRecording.getStackFrames()) {
            if (stackFrame.getLineNumber().equals(lineNumber)) {
                String value = stackFrame.getVariable(variableName);
                if (value != null) {
                    stringBuilder.append(value);
                    stringBuilder.append("; ");
                }
            }
        }
        return stringBuilder.toString();
    }

    public String getVariableValue(String variableName, Integer lineNumber) {
        StringBuilder stringBuilder = new StringBuilder();
        for (StackFrame stackFrame : stackRecording.getStackFrames()) {
            if (stackFrame.getLineNumber().equals(lineNumber)) {
                StackFrame nextStackFrame = stackFrame.getSuccessor();
                if (nextStackFrame != null) {
                    String value = nextStackFrame.getVariable(variableName);
                    if (value != null) {
                        stringBuilder.append(value);
                        stringBuilder.append("; ");
                    }
                }
            }
        }
        return stringBuilder.toString();
    }

    public void addComment(Integer lineNumber, String content){
        // Change the correct line from the source code
        String line = this.sourceCode.split("\n")[lineNumber - 1];
        // Add the comment
        line = line + " // " + content;
        // Replace the line in the source code
        String[] lines = this.sourceCode.split("\n");
        lines[lineNumber - 1] = line;
        this.sourceCode = String.join("\n", lines);
    }
}

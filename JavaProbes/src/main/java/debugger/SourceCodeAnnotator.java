package debugger;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;


import java.util.List;
import java.util.Map;


public class SourceCodeAnnotator {

    private final VariableMap stackTraces;

    private String sourceCode;

    private final String className;

    private final String methodName;

    private Boolean getLoopValue = false;

    public void setLoopValue(Boolean getLoopValue) {
        this.getLoopValue = getLoopValue;
    }

    SourceCodeAnnotator(VariableMap stackTraces, String sourceCode, String className, String methodName) {
        this.stackTraces = stackTraces;
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
        if (!stackTraces.valueMap.containsKey(lineNumber)) { // variable not defined or accessible from this line
            return "-";
        }
        List<String> values = stackTraces.extractVariable(variableName, stackTraces.valueMap.get(lineNumber));
        // Join them with | as a separator
        if (values == null) {
            return "null";
        }
        if (getLoopValue) { // In a loop/recursive, return all values
            return String.join("|", values);
        }
        else { // Not in a loop/recursive, return the last value
            return values.get(values.size() - 1);
        }

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

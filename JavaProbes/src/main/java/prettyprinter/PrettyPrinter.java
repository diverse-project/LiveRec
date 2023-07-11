package prettyprinter;

import debugger.StackRecording;
import debugger.VariableMap;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class PrettyPrinter {

    private final String sourcePath;

    private final String sourceCode;
    private final String debugClass;
    private final String debugFunction;

    public PrettyPrinter(String sourcePath, String debugClass, String debugFunction) {
        this.sourcePath = sourcePath;
        this.debugClass = debugClass;
        this.debugFunction = debugFunction;
        this.sourceCode = readSourceCode();
    }
    public String getResult(StackRecording variableMap) {
        SourceCodeAnnotator annotator = new SourceCodeAnnotator(variableMap, sourceCode, debugClass, debugFunction);
        return annotator.getSourceCode();
    }

    private String readSourceCode() {
        // Open the file of the debug class
        File file = new File(sourcePath + debugClass.replace(".", "/") + ".java");
        StringBuilder sourceCodeBuilder = new StringBuilder();
        // Read the file line by line
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            String line;
            while ((line = br.readLine()) != null) {
                sourceCodeBuilder.append(line).append("\n");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return sourceCodeBuilder.toString();
    }
}

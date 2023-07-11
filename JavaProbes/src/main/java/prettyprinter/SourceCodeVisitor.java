package prettyprinter;

import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.ReturnStmt;
import com.github.javaparser.ast.stmt.WhileStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class SourceCodeVisitor extends VoidVisitorAdapter<SourceCodeAnnotator> {

    @Override
    public void visit(ClassOrInterfaceDeclaration cd, SourceCodeAnnotator sourceCodeAnnotator) {
        if (!sourceCodeAnnotator.getClassName().contains(cd.getNameAsString())) {
            return;
        }
        super.visit(cd, sourceCodeAnnotator);
    }

    @Override
    public void visit(MethodDeclaration md, SourceCodeAnnotator sourceCodeAnnotator) {
        if (!md.getNameAsString().equals(sourceCodeAnnotator.getMethodName())) {
            return;
        }
        StringBuilder sb = new StringBuilder();
        md.getParameters().forEach(parameter -> {
            String value = sourceCodeAnnotator.getVariable(parameter.getNameAsString(), -1);
            sb.append(parameter.getNameAsString()).append(" = ").append(value);
            // if not last parameter add a comma
            if (md.getParameters().indexOf(parameter) != md.getParameters().size() - 1) {
                sb.append("; ");
            }
        });
        sourceCodeAnnotator.addComment(md.getBegin().get().line, sb.toString());
        super.visit(md, sourceCodeAnnotator);
    }


    @Override
    public void visit(VariableDeclarationExpr cu, SourceCodeAnnotator sourceCodeAnnotator) {
        String value = sourceCodeAnnotator.getVariableValue(cu.getVariable(0).getNameAsString(), cu.getBegin().get().line);
        sourceCodeAnnotator.addComment(cu.getBegin().get().line, cu.getVariable(0).getNameAsString() + " = " + value);
    }

    @Override
    public void visit(AssignExpr cu, SourceCodeAnnotator sourceCodeAnnotator) {
        String value = sourceCodeAnnotator.getVariableValue(cu.getTarget().asNameExpr().getNameAsString(), cu.getBegin().get().line);
        sourceCodeAnnotator.addComment(cu.getBegin().get().line, cu.getTarget().asNameExpr().getNameAsString() + " = " + value);
    }


    @Override
    public void visit(BinaryExpr cu, SourceCodeAnnotator sourceCodeAnnotator) {
        StringBuilder sb = new StringBuilder();
        if (cu.getLeft() instanceof NameExpr){
            sb.append(((NameExpr) cu.getLeft()).getNameAsString());
            sb.append(" = ");
            sb.append(sourceCodeAnnotator.getVariable(((NameExpr) cu.getLeft()).getNameAsString(), cu.getBegin().get().line));
            sb.append("| ");
        }
        if (cu.getRight() instanceof NameExpr){
            sb.append(((NameExpr) cu.getRight()).getNameAsString());
            sb.append(" = ");
            sb.append(sourceCodeAnnotator.getVariable(((NameExpr) cu.getRight()).getNameAsString(), cu.getBegin().get().line));
        }
        sourceCodeAnnotator.addComment(cu.getBegin().get().line, sb.toString());
    }



}

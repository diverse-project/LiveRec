package debugger;

import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.stmt.ReturnStmt;
import com.github.javaparser.ast.stmt.WhileStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class SourceCodeVisitor extends VoidVisitorAdapter<SourceCodeAnnotator> {

    private boolean inALoop = false;

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
    public void visit(ReturnStmt cu, SourceCodeAnnotator sourceCodeAnnotator) {
        String value = getValueTerminal(sourceCodeAnnotator, cu.getExpression().get(),  cu.getBegin().get().line);
        sourceCodeAnnotator.addComment(cu.getBegin().get().line, "return " + value);
    }

    @Override
    public void visit(VariableDeclarationExpr cu, SourceCodeAnnotator sourceCodeAnnotator) {
        String value = sourceCodeAnnotator.getVariable(cu.getVariable(0).getNameAsString(), cu.getBegin().get().line + 1);
        sourceCodeAnnotator.addComment(cu.getBegin().get().line, cu.getVariable(0).getNameAsString() + " = " + value);
    }

    @Override
    public void visit(WhileStmt cu, SourceCodeAnnotator sourceCodeAnnotator) {
        sourceCodeAnnotator.setLoopValue(true);
        super.visit(cu, sourceCodeAnnotator);
        sourceCodeAnnotator.setLoopValue(false);
    }

    @Override
    public void visit(AssignExpr cu, SourceCodeAnnotator sourceCodeAnnotator) {
        String value = sourceCodeAnnotator.getVariable(cu.getTarget().asNameExpr().getNameAsString(), cu.getBegin().get().line);
        sourceCodeAnnotator.addComment(cu.getBegin().get().line, cu.getTarget().asNameExpr().getNameAsString() + " = " + value);
    }

    @Override
    public void visit(BinaryExpr cu, SourceCodeAnnotator sourceCodeAnnotator) {
        String valueLeft = getValueTerminal(sourceCodeAnnotator, cu.getLeft(), cu.getBegin().get().line);
        String valueRight = getValueTerminal(sourceCodeAnnotator, cu.getRight(), cu.getBegin().get().line);
        sourceCodeAnnotator.addComment(cu.getBegin().get().line, getNameTerminals(cu.getLeft()) + "=" + valueLeft + " " + cu.getOperator().asString() + " " + getNameTerminals(cu.getRight()) + " = " + valueRight);
    }

    private String getValueTerminal(SourceCodeAnnotator src, Expression expression, int line){
        if (expression.isNameExpr()) {
            return src.getVariable(expression.asNameExpr().getNameAsString(), line);
        }
        else{
            return getNameTerminals(expression);
        }
    }

    private String getNameTerminals(Expression expression) {
        if (expression.isNameExpr()) {
            return expression.asNameExpr().getNameAsString();
        }
        if (expression.isIntegerLiteralExpr()) {
            return expression.asIntegerLiteralExpr().getValue();
        }
        if (expression.isStringLiteralExpr()) {
            return expression.asStringLiteralExpr().getValue();
        }
        if (expression.isBooleanLiteralExpr()) {
            return expression.asBooleanLiteralExpr().toString();
        }
        if (expression.isCharLiteralExpr()) {
            return expression.asCharLiteralExpr().getValue();
        }
        if (expression.isDoubleLiteralExpr()) {
            return expression.asDoubleLiteralExpr().getValue();
        }
        if (expression.isLongLiteralExpr()) {
            return expression.asLongLiteralExpr().getValue();
        }
        if (expression.isNullLiteralExpr()) {
            return "null";
        }
        if (expression.isUnaryExpr()) {
            return expression.asUnaryExpr().getOperator().asString() + getNameTerminals(expression.asUnaryExpr().getExpression());
        }
        return "undefined expression";
    }




}

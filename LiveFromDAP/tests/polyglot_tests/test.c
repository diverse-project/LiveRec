double foo() {
    return polyglotEval("py", "/code/tests/polyglot_tests/test2.py");
}


int main() {
    int x = 10;
    double y = foo();
    return x;
}
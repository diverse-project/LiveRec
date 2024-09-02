double foo() {
    return polyglotEval("py", "/code/src/livefromdap/runner/test.py");
}


int main() {
    int x = 10;
    double y = foo();
    return x;
}
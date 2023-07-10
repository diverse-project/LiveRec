EXAMPLES_C_SOURCES = $(wildcard target/c/*.c)
EXAMPLES_C_TARGETS = $(EXAMPLES_C_SOURCES:target/c/%.c=target/c/%.so)

EXAMPLES_JAVA_SOURCES = $(wildcard target/java/*.java)
EXAMPLES_JAVA_TARGETS = $(EXAMPLES_JAVA_SOURCES:target/java/%.java=target/java/%.class)

RUNNER_C_SOURCES = $(wildcard runner/c_runner.c)
RUNNER_C_TARGETS = $(RUNNER_C_SOURCES:runner/%.c=runner/%)

RUNNER_JAVA_SOURCES = $(wildcard runner/Runner.java)
RUNNER_JAVA_TARGETS = $(RUNNER_JAVA_SOURCES:runner/%.java=runner/bin/%.class)

.PHONY: all examples runner clean

examples: $(EXAMPLES_C_TARGETS) $(EXAMPLES_JAVA_TARGETS)

runner: $(RUNNER_C_TARGETS) $(RUNNER_JAVA_TARGETS)

all : examples runner

target/c/%.so: target/c/%.c
	gcc -g -fPIC -shared -o $@ $<

target/java/%.class: target/java/%.java
	javac -g $<

runner/%: runner/%.c
	gcc -g -o $@ $<

runner/bin/Runner.class: runner/Runner.java runner/bin/DynamicClassLoader.class runner/bin/DynamicClassLoaderFactory.class
	javac -g -d runner/bin -cp runner/bin runner/Runner.java

runner/bin/DynamicClassLoader.class: runner/DynamicClassLoader.java
	javac -g -d runner/bin -cp runner/bin runner/DynamicClassLoader.java

runner/bin/DynamicClassLoaderFactory.class: runner/DynamicClassLoaderFactory.java runner/bin/DynamicClassLoader.class
	javac -g -d runner/bin -cp runner/bin runner/DynamicClassLoaderFactory.java


clean:
	rm -f $(EXAMPLES_C_TARGETS) $(EXAMPLES_JAVA_TARGETS) runner/c_runner runner/bin/*.class
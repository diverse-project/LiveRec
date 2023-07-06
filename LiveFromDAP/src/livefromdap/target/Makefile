C_SOURCES = $(wildcard c/*.c)
C_TARGETS = $(C_SOURCES:c/%.c=c/%.so)

JAVA_SOURCES = $(wildcard java/*.java)
JAVA_TARGETS = $(JAVA_SOURCES:java/%.java=java/%.class)

.PHONY: all clean

all: $(C_TARGETS) $(JAVA_TARGETS)

c/%.so: c/%.c
	gcc -g -fPIC -shared -o $@ $<

java/%.class: java/%.java
	javac -g $<

clean:
	rm -f $(C_TARGETS) $(JAVA_TARGETS)
# The Computer Language Benchmarks Game
# https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
#
# Translated from Mr Ledrug's C program by Jeremy Zerfas.
# Transliterated from GMP to built-in by Isaac Gouy

tmp1 = 0
tmp2 = 0

acc = 0
den = 1
num = 1


#@ex1: extract_Digit(3)
def extract_Digit(nth):
    global tmp1, tmp2, acc, den, num
    tmp1 = num * nth
    #@ex1: probe : tmp1
    #@ex1: probe : acc
    tmp2 = tmp1 + acc
    tmp1 = tmp2 // den

    return tmp1

#@ex2: eliminate_Digit(4)
def eliminate_Digit(d):
    global acc, den, num
    acc = acc - den * d
    #@ex2: probe : acc
    acc = acc * 10
    #@ex2: probe : acc
    num = num * 10

#@ex3: next_Term(2)
def next_Term(k):
    global acc, den, num
    k2=k*2+1
    #@ex3: probe : k2
    acc = acc + num * 2
    acc = acc * k2
    den = den * k2
    #@ex3: probe : den
    num = num * k

#@ex4:main()
def main():
    polyglotEval("js", "/code/tests/benchmarks/pidigits/loop_replace/pidigits_lib.js")
    polyglotEval("js", "/code/tests/benchmarks/pidigits/loop_replace/loop.js")
    #@ex4: probe JS : acc
    #@ex4: probe JS : ns
    #@ex4: probe JS.pad : count

    



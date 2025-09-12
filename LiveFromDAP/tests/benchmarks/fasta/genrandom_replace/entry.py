# The Computer Language Benchmarks Game
# https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
#
# modified by Ian Osgood
# modified again by Heinrich Acker
# modified by Justin Peel
# 2to3

import sys, bisect


alu = (
   'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
   'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
   'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
   'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
   'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
   'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
   'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA')

iub = list(zip('acgtBDHKMNRSVWY', [0.27, 0.12, 0.12, 0.27] + [0.02]*11))

homosapiens = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008),
]


def genRandom(ia = 3877, ic = 29573, im = 139968):
    seed = 42
    imf = float(im)
    while 1:
        seed = (seed * ia + ic) % im
        #@ex1: probe : seed
        yield polyglotEval("js", "/code/tests/benchmarks/fasta/genrandom_replace/rand.js")

Random = genRandom()

#@ex2: makeCumulative(iub)
def makeCumulative(table):
    P = []
    C = []
    prob = 0.
    for char, p in table:
        prob += p
        #@ex2: probe : prob
        P += [prob]
        C += [char]
    #@ex1: probe : C
    return (P, C)

def repeatFasta(src, n):
    width = 60
    r = len(src)
    #@ex1: probe : r
    s = src + src + src[:n % r]
    for j in range(n // width):
        i = j*width % r
        #@ex1: probe : s if £ j < 5 £
        print(s[i:i+width])
    if n % width:
        print(s[-(n % width):])

def randomFasta(table, n):
    width = 60
    r = range(width)
    #@ex1: probe : r
    gR = Random.__next__
    bb = bisect.bisect
    jn = ''.join
    probs, chars = makeCumulative(table)
    for j in range(n // width):
        x = jn([chars[bb(probs, gR())] for i in r])
        #@ex1: probe : r
        print(x)
    if n % width:
        print(jn([chars[bb(probs, gR())] for i in range(n % width)]))
        #@ex1: probe : probs

#@ex1: main(10)
def main(n):
    # n = 10
    polyglotEval("js", "/code/tests/benchmarks/fasta/genrandom_replace/rand_lib.js")

    print('>ONE Homo sapiens alu')
    repeatFasta(alu, n*2)

    print('>TWO IUB ambiguity codes')
    randomFasta(iub, n*3)
    #@ex1: probe JS : last
    #@ex1: probe JS.rand : max
    print('>THREE Homo sapiens frequency')
    randomFasta(homosapiens, n*5)
    #@ex1: probe JS.rand : last



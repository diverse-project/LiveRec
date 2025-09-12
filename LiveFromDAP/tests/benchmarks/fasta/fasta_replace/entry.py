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
        yield seed / imf

Random = genRandom()

def makeCumulative(table):
    P = []
    C = []
    prob = 0.
    for char, p in table:
        prob += p
        P += [prob]
        C += [char]
    return (P, C)

def repeatFasta(src, n):
    width = 60
    r = len(src)
    s = src + src + src[:n % r]
    for j in range(n // width):
        i = j*width % r
        print(s[i:i+width])
    if n % width:
        print(s[-(n % width):])

def randomFasta(table, n):
    width = 60
    r = range(width)
    gR = Random.__next__
    bb = bisect.bisect
    jn = ''.join
    probs, chars = makeCumulative(table)
    for j in range(n // width):
        x = jn([chars[bb(probs, gR())] for i in r])
        print(x)
    if n % width:
        print(jn([chars[bb(probs, gR())] for i in range(n % width)]))

#@ex1: main(10)
def main(n):
    # n = 10000000
    polyglotEval("js", "/code/tests/benchmarks/fasta/fasta_replace/fasta_lib.js")
    print('>ONE Homo sapiens alu')
    polyglotEval("js", "/code/tests/benchmarks/fasta/fasta_replace/HOMO.js")# repeatFasta(alu, n*2)
    #@ex1: probe JS : n
    #@ex1: probe JS.fastaRepeat : lenOut
    #@ex1: probe JS.fastaRepeat : seqi
    print('>TWO IUB ambiguity codes')
    polyglotEval("js", "/code/tests/benchmarks/fasta/fasta_replace/IUB.js")
    #@ex1: probe JS.fastaRandom : line
    #@ex1: probe JS.makeCumulative : last
    # randomFasta(iub, n*3)
    print('>THREE Homo sapiens frequency')
    polyglotEval("js", "/code/tests/benchmarks/fasta/fasta_replace/FREQ.js")
    #@ex1: probe JS : n
    #@ex1: probe JS.fastaRandom : line
    #@ex1: probe JS.makeCumulative : last
    # randomFasta(homosapiens, n*5)



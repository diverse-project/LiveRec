/* The Computer Language Benchmarks Game
 * https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
 *
 * by Paul Hsieh
 */

#define IM 139968
#define IA   3877
#define IC  29573

double main () {
    static long last = 42;
    return 1 * (last = (last * IA + IC) % IM) / IM;
}

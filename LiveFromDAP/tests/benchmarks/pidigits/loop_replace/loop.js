/* The Computer Language Benchmarks Game
   https://salsa.debian.org/benchmarksgame-team/benchmarksgame/

   contributed by Denis Gribov
   based on C source code by Ledhug
   un-buffered by Isaac Gouy
   
*/


const n = 30;

var i = 0, ns = 0;
var k = 0;
var k2 = 1;
var acc = 0n;
var den = 1n;
var num = 1n;
var tmp = 0n;
var d3 = 0n;
var d4 = 0n;

while (i < n) {
  k++;
  // next term
  k2 += 2;

  acc += num * 2n;
  acc *= BigInt(k2);
  den *= BigInt(k2);
  num *= BigInt(k);
  // next term end
  if (num > acc) {
    continue;
  }

  // extract digit
  tmp = num * 3n;
  tmp = tmp + acc;
  d3 = tmp / den;

  tmp = tmp + num;
  d4 = tmp / den;

  if (d3 !== d4) {
    continue;
  }
  // extract digit end

  const d = Number(d3);
  ns = ns * 10 + d;
  i++;
  let last = i >= n;
  if (i % 10 == 0 || last) {
    console.log(pad(ns, last) + '\t:' + i);   
    ns = 0;
  }

  if (last) break;

  acc -= den * BigInt(d);
  acc *= 10n;
  num *= 10n;
}


module.exports = ns

console.log("hi")
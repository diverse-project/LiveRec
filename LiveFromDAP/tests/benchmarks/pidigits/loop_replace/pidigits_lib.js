
function pad(i, last) {
  var res = i.toString(), count;
  count = 10 - res.length;
  while (count > 0) {
  last ? res += ' ' : res = '0' + res;
  count--;
  }
  return res;
}
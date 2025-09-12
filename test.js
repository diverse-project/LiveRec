
function square(number) {
    var t1 = 2;
    for (let index = 0; index < 5; index++) {
        t1 = t1 + 1;
    }
    var t2 = foo(3);
    return number * number;
}

var t0 = 42;

function foo(number) {
    var t3 = number * 2;
    return t3 + 1;
}

var res = square(5);

module.exports = res;

var moment = require('moment'); // require

//@ex1:add_short_reverse_args()
function add_short_reverse_args() {
    var a = moment(),
        b,
        c,
        d;
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add({ ms: 50 }).milliseconds();
    //@ex1:probe : val
    var val = a.add({ s: 1 }).seconds();
    //@ex1:probe : val
    var val = a.add({ m: 1 }).minutes();
    //@ex1:probe : val
    var val = a.add({ h: 1 }).hours();
    //@ex1:probe : val
    var val = a.add({ d: 1 }).date();
    //@ex1:probe : val
    var val = a.add({ w: 1 }).date();
    //@ex1:probe : val
    var val = a.add({ M: 1 }).month();
    //@ex1:probe : val
    var val = a.add({ y: 1 }).year();
    //@ex1:probe : val
    var val = a.add({ Q: 1 }).month();
    //@ex1:probe : val

    b = moment([2010, 0, 31]).add({ M: 1 });
    c = moment([2010, 1, 28]).subtract({ M: 1 });
    d = moment([2010, 1, 28]).subtract({ Q: 1 });

    var val = b.month();
    //@ex1:probe : val
    var val = b.date();
    //@ex1:probe : val
    var val = c.month();
    //@ex1:probe : val
    var val = c.date();
    //@ex1:probe : val
    var val = d.month();
    //@ex1:probe : val
    var val = d.date();
    //@ex1:probe : val
    var val = d.year();
    //@ex1:probe : val
}

//@ex2:add_long_reverse_args()
function add_long_reverse_args() {
    var a = moment();
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add({ milliseconds: 50 }).milliseconds();
    //@ex2:probe : val
    var val = a.add({ seconds: 1 }).seconds();
    //@ex2:probe : val
    var val = a.add({ minutes: 1 }).minutes();
    //@ex2:probe : val
    var val = a.add({ hours: 1 }).hours();
    //@ex2:probe : val
    var val = a.add({ days: 1 }).date();
    //@ex2:probe : val
    var val = a.add({ weeks: 1 }).date();
    //@ex2:probe : val
    var val = a.add({ months: 1 }).month();
    //@ex2:probe : val
    var val = a.add({ years: 1 }).year();
    //@ex2:probe : val
    var val = a.add({ quarters: 1 }).month();
    //@ex2:probe : val
}

//@ex3:add_long_singular_reverse_args()
function add_long_singular_reverse_args() {
    var a = moment();
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add({ millisecond: 50 }).milliseconds();
    //@ex2:probe : val
    var val = a.add({ second: 1 }).seconds();
    //@ex2:probe : val
    var val = a.add({ minute: 1 }).minutes();
    //@ex2:probe : val
    var val = a.add({ hour: 1 }).hours();
    //@ex2:probe : val
    var val = a.add({ day: 1 }).date();
    //@ex2:probe : val
    var val = a.add({ week: 1 }).date();
    //@ex2:probe : val
    var val = a.add({ month: 1 }).month();
    //@ex2:probe : val
    var val = a.add({ year: 1 }).year();
    //@ex2:probe : val
    var val = a.add({ quarter: 1 }).month();
    //@ex2:probe : val
}

//@ex3:add_string_long_reverse_args()
function add_string_long_reverse_args() {
    var a = moment(),b;

    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    b = a.clone();

    var val = a.add('millisecond', 50).milliseconds();
    //@ex3:probe : val
    var val = a.add('second', 1).seconds();
    //@ex3:probe : val
    var val = a.add('minute', 1).minutes();
    //@ex3:probe : val
    var val = a.add('hour', 1).hours();
    //@ex3:probe : val
    var val = a.add('day', 1).date();
    //@ex3:probe : val
    var val = a.add('week', 1).date();
    //@ex3:probe : val
    var val = a.add('month', 1).month();
    //@ex3:probe : val
    var val = a.add('year', 1).year();
    //@ex3:probe : val
    var val = b.add('day', '01').date();
    //@ex3:probe : val
    var val = a.add('quarter', 1).month();
    //@ex3:probe : val
}

//@ex4:add_string_long_singular_reverse_args()
function add_string_long_singular_reverse_args() {
    var a = moment(),
        b;


    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    b = a.clone();

    var val = a.add('milliseconds', 50).milliseconds();
    //@ex4: probe : val
    var val = a.add('seconds', 1).seconds();
    //@ex4: probe : val
    var val = a.add('minutes', 1).minutes();
    //@ex4: probe : val
    var val = a.add('hours', 1).hours();
    //@ex4: probe : val
    var val = a.add('days', 1).date();
    //@ex4: probe : val
    var val = a.add('weeks', 1).date();
    //@ex4: probe : val
    var val = a.add('months', 1).month();
    //@ex4: probe : val
    var val = a.add('years', 1).year();
    //@ex4: probe : val
    var val = b.add('days', '01').date();
    //@ex4: probe : val
    var val = a.add('quarters', 1).month();
    //@ex4: probe : val
}

//@ex5:add_string_short_reverse_args()
function add_string_short_reverse_args() {
    var a = moment();

    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

   a.add('ms', 50).milliseconds();
   //@ex4: probe : val
   a.add('s', 1).seconds();
   //@ex4: probe : val
   a.add('m', 1).minutes();
   //@ex4: probe : val
   a.add('h', 1).hours();
   //@ex4: probe : val
   a.add('d', 1).date();
   //@ex4: probe : val
   a.add('w', 1).date();
   //@ex4: probe : val
   a.add('M', 1).month();
   //@ex4: probe : val
   a.add('y', 1).year();
   //@ex4: probe : val
   a.add('Q', 1).month();
   //@ex4: probe : val
}

//@ex5:add_string_long()
function add_string_long() {
    var a = moment();
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add(50, 'millisecond').milliseconds();
    //@ex5: probe : val
    var val = a.add(1, 'second').seconds();
    //@ex5: probe : val
    var val = a.add(1, 'minute').minutes();
    //@ex5: probe : val
    var val = a.add(1, 'hour').hours();
    //@ex5: probe : val
    var val = a.add(1, 'day').date();
    //@ex5: probe : val
    var val = a.add(1, 'week').date();
    //@ex5: probe : val
    var val = a.add(1, 'month').month();
    //@ex5: probe : val
    var val = a.add(1, 'year').year();
    //@ex5: probe : val
    var val = a.add(1, 'quarter').month();
    //@ex5: probe : val
}

//@ex6:add_string_long_singular()
function add_string_long_singular() {
    var a = moment();
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add(50, 'milliseconds').milliseconds();
    //@ex6: probe : val
    var val = a.add(1, 'seconds').seconds();
    //@ex6: probe : val
    var val = a.add(1, 'minutes').minutes();
    //@ex6: probe : val
    var val = a.add(1, 'hours').hours();
    //@ex6: probe : val
    var val = a.add(1, 'days').date();
    //@ex6: probe : val
    var val = a.add(1, 'weeks').date();
    //@ex6: probe : val
    var val = a.add(1, 'months').month();
    //@ex6: probe : val
    var val = a.add(1, 'years').year();
    //@ex6: probe : val
    var val = a.add(1, 'quarters').month();
    //@ex6: probe : val
}

//@ex7:add_string_short()
function add_string_short() {
    var a = moment();
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add(50, 'ms').milliseconds();
    //@ex7: probe : val
    var val = a.add(1, 's').seconds();
    //@ex7: probe : val
    var val = a.add(1, 'm').minutes();
    //@ex7: probe : val
    var val = a.add(1, 'h').hours();
    //@ex7: probe : val
    var val = a.add(1, 'd').date();
    //@ex7: probe : val
    var val = a.add(1, 'w').date();
    //@ex7: probe : val
    var val = a.add(1, 'M').month();
    //@ex7: probe : val
    var val = a.add(1, 'y').year();
    //@ex7: probe : val
    var val = a.add(1, 'Q').month();
    //@ex7: probe : val
}

//@ex8:add_strings_string_short_reversed()
function add_strings_string_short_reversed() {
    var a = moment();

    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add('ms', '50').milliseconds();
    //@ex8: probe : val
    var val = a.add('s', '1').seconds();
    //@ex8: probe : val
    var val = a.add('m', '1').minutes();
    //@ex8: probe : val
    var val = a.add('h', '1').hours();
    //@ex8: probe : val
    var val = a.add('d', '1').date();
    //@ex8: probe : val
    var val = a.add('w', '1').date();
    //@ex8: probe : val
    var val = a.add('M', '1').month();
    //@ex8: probe : val
    var val = a.add('y', '1').year();
    //@ex8: probe : val
    var val = a.add('Q', '1').month();
    //@ex8: probe : val
}

//@ex9:subtract_strings_string_short_reversed()
function subtract_strings_string_short_reversed() {
    var a = moment();

    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.subtract('ms', '50').milliseconds();
    //@ex9: probe : val
    var val = a.subtract('s', '1').seconds();
    //@ex9: probe : val
    var val = a.subtract('m', '1').minutes();
    //@ex9: probe : val
    var val = a.subtract('h', '1').hours();
    //@ex9: probe : val
    var val = a.subtract('d', '1').date();
    //@ex9: probe : val
    var val = a.subtract('w', '1').date();
    //@ex9: probe : val
    var val = a.subtract('M', '1').month();
    //@ex9: probe : val
    var val = a.subtract('y', '1').year();
    //@ex9: probe : val
    var val = a.subtract('Q', '1').month();
    //@ex9: probe : val
}

//@ex10:add_strings_string_short()
function add_strings_string_short() {
    var a = moment();
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add('50', 'ms').milliseconds();
    //@ex10: probe : val
    var val = a.add('1', 's').seconds();
    //@ex10: probe : val
    var val = a.add('1', 'm').minutes();
    //@ex10: probe : val
    var val = a.add('1', 'h').hours();
    //@ex10: probe : val
    var val = a.add('1', 'd').date();
    //@ex10: probe : val
    var val = a.add('1', 'w').date();
    //@ex10: probe : val
    var val = a.add('1', 'M').month();
    //@ex10: probe : val
    var val = a.add('1', 'y').year();
    //@ex10: probe : val
    var val = a.add('1', 'Q').month();
    //@ex10: probe : val
}

//@ex11:add_no_string_with_milliseconds_default()
function add_no_string_with_milliseconds_default() {
    var a = moment();
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.add(50).milliseconds();
    //@ex11: probe : val
}

//@ex12:subtract_strings_string_short()
function subtract_strings_string_short() {
    var a = moment();
    a.year(2011);
    a.month(9);
    a.date(12);
    a.hours(6);
    a.minutes(7);
    a.seconds(8);
    a.milliseconds(500);

    var val = a.subtract('50', 'ms').milliseconds();
    //@ex12:probe : val
    var val = a.subtract('1', 's').seconds();
    //@ex12:probe : val
    var val = a.subtract('1', 'm').minutes();
    //@ex12:probe : val
    var val = a.subtract('1', 'h').hours();
    //@ex12:probe : val
    var val = a.subtract('1', 'd').date();
    //@ex12:probe : val
    var val = a.subtract('1', 'w').date();
    //@ex12:probe : val
    var val = a.subtract('1', 'M').month();
    //@ex12:probe : val
    var val = a.subtract('1', 'y').year();
    //@ex12:probe : val
    var val = a.subtract('1', 'Q').month();
    //@ex12:probe : val
}

//@ex13:add_across_DST()
function add_across_DST() {
    // Detect Safari bug and bail. Hours on 13th March 2011 are shifted
    // with 1 ahead.
    if (new Date(2011, 2, 13, 5, 0, 0).getHours() !== 5) {
        return;
    }

    var a = moment(new Date(2011, 2, 12, 5, 0, 0)),
        b = moment(new Date(2011, 2, 12, 5, 0, 0)),
        c = moment(new Date(2011, 2, 12, 5, 0, 0)),
        d = moment(new Date(2011, 2, 12, 5, 0, 0)),
        e = moment(new Date(2011, 2, 12, 5, 0, 0));
    a.add(1, 'days');
    b.add(24, 'hours');
    c.add(1, 'months');
    e.add(1, 'quarter');

    var val = a.hours();
    //@ex13:probe : val
    if (b.isDST() && !d.isDST()) {
        var val = b.hours();
        //@ex13:probe : val
    } else if (!b.isDST() && d.isDST()) {
        var val = b.hours();
        //@ex13:probe : val
    } else {
        var val = b.hours();
        //@ex13:probe : val
    }
    var val = c.hours();
    //@ex13:probe : val
    var val = e.hours();
    //@ex13:probe : val
}

//@ex14:add_decimal_values_of_days_and_months()
function add_decimal_values_of_days_and_months() {
    var val = 
        moment([2016, 3, 3]).add(1.5, 'days').date();
    //@ex14:probe : val   
    var val = 
        moment([2016, 3, 3]).add(-1.5, 'days').date();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 1]).add(-1.5, 'days').date();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 3]).add(1.5, 'months').month();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 3]).add(-1.5, 'months').month();
    //@ex14:probe : val
    var val = 
        moment([2016, 0, 3]).add(-1.5, 'months').month();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 3]).subtract(1.5, 'days').date();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 2]).subtract(1.5, 'days').date();
    //@ex14:probe : val
    var val = 
        moment([2016, 1, 1]).subtract(1.1, 'days').date();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 3]).subtract(-1.5, 'days').date();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 30]).subtract(-1.5, 'days').date();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 3]).subtract(1.5, 'months').month();
    //@ex14:probe : val
    var val = 
        moment([2016, 3, 3]).subtract(-1.5, 'months').month();
    //@ex14:probe : val
    var val = 
        moment([2016, 11, 31]).subtract(-1.5, 'months').month();
    //@ex14:probe : val
    var val = 
        moment([2016, 0, 1]).add(1.5, 'years').format('YYYY-MM-DD');
    //@ex14:probe : val
    var val = 
        moment([2016, 0, 1]).add(1.6, 'years').format('YYYY-MM-DD');
    //@ex14:probe : val
    var val = 
        moment([2016, 0, 1]).add(1.1, 'quarters').format('YYYY-MM-DD');
    //@ex14:probe : val
}

//@ex15:add_subtract_ISO_week()
function add_subtract_ISO_week() {
    var val =
        moment([2016, 3, 15]).subtract(1, 'W').date();
    //@ex15:probe : val
    var val =
        moment([2016, 3, 15]).subtract(1, 'isoweek').date();
    //@ex15:probe : val
    var val =
        moment([2016, 3, 15]).subtract(1, 'isoweeks').date();
    //@ex15:probe : val

    var val =
        moment([2016, 3, 15]).add(1, 'W').date();
    //@ex15:probe : val
    var val =
        moment([2016, 3, 15]).add(1, 'isoweek').date();
    //@ex15:probe : val
    var val =
        moment([2016, 3, 15]).add(1, 'isoweeks').date();
    //@ex15:probe : val
}
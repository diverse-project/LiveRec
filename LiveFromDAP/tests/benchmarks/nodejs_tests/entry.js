
//@ex1:test_array()
function test_array() {

    const array = [
        1,
        9,
        48,
        13493,
        9459324,
        { name: 'hello' },
        [
            'world',
            'node',
            'abi',
        ],
    ];



    array.forEach(function (element, index) {
        let val = array[index];
        //@ex1:probe : val
    });


    //@ex1: probe : array

    let val1 = 0 in array;
    //@ex1:probe : val1
    let val2 = array.length + 1 in array;
    //@ex1:probe : val2


    
    // Verify that array elements can be deleted.
    const arr = ['a', 'b', 'c', 'd'];

    let val3 = arr.length
    //@ex1: probe : val3
    let val4 = 2 in arr;
    //@ex1: probe : val4
    arr.splice(2);
    let val5 = arr.length;
    //@ex1: probe : val5
    let val6 = 2 in arr;
    //@ex1: probe : val6
    
}

//@ex2:test_date()
function test_date() {
    const dateTypeTestDate = new Date(1549183351);
    let val1 = dateTypeTestDate instanceof Date;
    //@ex2:probe : val1

    let val2 = 2.4 instanceof Date;
    //@ex2:probe : val2
    let val3 = 'not a date' instanceof Date;
    //@ex2:probe : val3
    let val4 = undefined instanceof Date;
    //@ex2:probe : val4
    let val5 = null instanceof Date;
    //@ex2:probe : val5
    let val6 = {} instanceof Date;
    //@ex2:probe : val6

    let val7 = new Date(1549183351).getUTCMilliseconds()
    //@ex2:probe : val7

}

//@ex3:test_number()
function test_number() {

    var val = 0;
    //@ex3:probe : val
    var val = -0;
    //@ex3:probe : val
    var val = 1;
    //@ex3:probe : val
    var val = -1;
    //@ex3:probe : val
    var val = 100;
    //@ex3:probe : val
    var val = 2121;
    //@ex3:probe : val
    var val = -1233;
    //@ex3:probe : val
    var val = 986583;
    //@ex3:probe : val
    var val = -976675;
    //@ex3:probe : val

    /* eslint-disable no-loss-of-precision */
    var val = 
        98765432213456789876546896323445679887645323232436587988766545658;
    //@ex3:probe : val
    var val = 
        -4350987086545760976737453646576078997096876957864353245245769809;
    //@ex3:probe : val
    /* eslint-enable no-loss-of-precision */
    var val = Number.MIN_SAFE_INTEGER;
    //@ex3:probe : val
    var val = Number.MAX_SAFE_INTEGER;
    //@ex3:probe : val
    var val = Number.MAX_SAFE_INTEGER + 10;
    //@ex3:probe : val

    var val = Number.MIN_VALUE;
    //@ex3:probe : val
    var val = Number.MAX_VALUE;
    //@ex3:probe : val
    var val = Number.MAX_VALUE + 10;
    //@ex3:probe : val

    var val = Number.POSITIVE_INFINITY;
    //@ex3:probe : val
    var val = Number.NEGATIVE_INFINITY;
    //@ex3:probe : val
    var val = Number.NaN;
    //@ex3:probe : val

    // Test zero
    var val =  0.0;
    //@ex3:probe : val
    var val = -0.0;
    //@ex3:probe : val

    // Test overflow scenarios
    var val = 4294967295;
    //@ex3:probe : val
    var val = 4294967296;
    //@ex3:probe : val
    var val = 4294967297;
    //@ex3:probe : val
    var val = 17 * 4294967296 + 1;
    //@ex3:probe : val
    var val = -1;
    //@ex3:probe : val

    // Validate documented behavior when value is retrieved as 32-bit integer with
    // `napi_get_value_int32`


    // Test min/max int32 range
    var val = (-Math.pow(2, 31));
    //@ex3:probe : val
    var val = (Math.pow(2, 31) - 1);
    //@ex3:probe : val

    // Test overflow scenarios
    var val = 4294967297;
    //@ex3:probe : val
    var val = 4294967296;
    //@ex3:probe : val
    var val = 4294967295;
    //@ex3:probe : val
    var val = 4294967296 * 5 + 3;
    //@ex3:probe : val

    // Test min/max safe integer range
    var val = Number.MIN_SAFE_INTEGER;
    //@ex3:probe : val
    var val = Number.MAX_SAFE_INTEGER;
    //@ex3:probe : val

    // Test within int64_t range (with precision loss)
    var val = -Math.pow(2, 63) + (Math.pow(2, 9) + 1);
    //@ex3:probe : val
    var val = Math.pow(2, 63) - (Math.pow(2, 9) + 1);
    //@ex3:probe : val

    // Test min/max double value
    var val = -Number.MIN_VALUE;
    //@ex3:probe : val
    var val = Number.MIN_VALUE;
    //@ex3:probe : val
    var val = -Number.MAX_VALUE;
    //@ex3:probe : val
    var val = Number.MAX_VALUE;
    //@ex3:probe : val

    // Test outside int64_t range
    var val = -Math.pow(2, 63) + (Math.pow(2, 9));
    //@ex3:probe : val
    var val = Math.pow(2, 63) - (Math.pow(2, 9));
    //@ex3:probe : val

    // Test non-finite numbers
    var val = Number.POSITIVE_INFINITY;
    //@ex3:probe : val
    var val = Number.NEGATIVE_INFINITY;
    //@ex3:probe : val
    var val = Number.NaN;
    //@ex3:probe : val

    // Validate documented behavior when value is retrieved as 64-bit integer with
    // `napi_get_value_int64`

    // Both V8 and ChakraCore return a sentinel value of `0x8000000000000000` when
    // the conversion goes out of range, but V8 treats it as unsigned in some cases.
    const RANGEERROR_POSITIVE = Math.pow(2, 63);
    const RANGEERROR_NEGATIVE = -Math.pow(2, 63);

    // Test zero
    var val = 0.0;
    //@ex3:probe : val
    var val = -0.0;
    //@ex3:probe : val

    // Test min/max safe integer range
    var val = Number.MIN_SAFE_INTEGER;
    var val = Number.MAX_SAFE_INTEGER;

    // Test within int64_t range (with precision loss)
    var val = -Math.pow(2, 63) + (Math.pow(2, 9) + 1);
    var val = Math.pow(2, 63) - (Math.pow(2, 9) + 1);

    // Test min/max double value
    var val = -Number.MIN_VALUE;
    //@ex3:probe : val
    var val = Number.MIN_VALUE;
    //@ex3:probe : val
    var val = -Number.MAX_VALUE;
    //@ex3:probe : val
    var val = Number.MAX_VALUE;
    //@ex3:probe : val

    // Test outside int64_t range
    var val = -Math.pow(2, 63) + (Math.pow(2, 9));
    //@ex3:probe : val
    var val = Math.pow(2, 63) - (Math.pow(2, 9));
    //@ex3:probe : val

    // Test non-finite numbers
    var val = Number.POSITIVE_INFINITY;
    //@ex3:probe : val
    var val = Number.NEGATIVE_INFINITY;
    //@ex3:probe : val
    var val = Number.NaN;
    //@ex3:probe : val
}

//@ex4:test_object()
function test_object() {

    const object = {
        hello: 'world',
        array: [
            1, 94, 'str', 12.321, { test: 'obj in arr' },
        ],
        newObject: {
            test: 'obj in obj',
        },
    };

    var val = object['hello'];
    //@ex4:probe : val
    var val = object.hello;
    //@ex4:probe : val
    var val = object['array'];
    //@ex4:probe : val
    var val = object['newObject'];
    //@ex4:probe : val

    var val = Object.hasOwn(object, 'hello');
    //@ex4:probe : val
    var val = Object.hasOwn(object, 'array');
    //@ex4:probe : val
    var val = Object.hasOwn(object, 'newObject');
    //@ex4:probe : val

    const newObject = new Object();
    var val = Object.hasOwn(newObject, 'test_number');
    //@ex4:probe : val
    var val = newObject.test_number;
    //@ex4:probe : val
    var val = newObject.test_string;
    //@ex4:probe : val

    {
        // Verify that napi_get_property() walks the prototype chain.
        var MyObject = function() {
            this.foo = 42;
            this.bar = 43;
        }

        MyObject.prototype.bar = 44;
        MyObject.prototype.baz = 45;

        const obj = new MyObject();

        var val = obj['foo'];
        //@ex4:probe : val
        var val = obj['bar'];
        //@ex4:probe : val
        var val = obj['baz'];
        //@ex4:probe : val
        var val = obj['toString'];
        //@ex4:probe : val

    }



    {
        // Verify that napi_has_own_property() does not walk the prototype chain.
        const symbol1 = Symbol();
        const symbol2 = Symbol();

        var MyObject = function() {
            this.foo = 42;
            this.bar = 43;
            this[symbol1] = 44;
        }

        MyObject.prototype.bar = 45;
        MyObject.prototype.baz = 46;
        MyObject.prototype[symbol2] = 47;

        const obj = new MyObject();

        var val = Object.hasOwn(obj, 'foo');
        //@ex4:probe : val
        var val = Object.hasOwn(obj, 'bar');
        //@ex4:probe : val
        var val = Object.hasOwn(obj, symbol1);
        //@ex4:probe : val
        var val = Object.hasOwn(obj, 'baz');
        //@ex4:probe : val
        var val = Object.hasOwn(obj, 'toString');
        //@ex4:probe : val
        var val = Object.hasOwn(obj, symbol2);
        //@ex4:probe : val

    }

    {
        // test_object.Inflate increases all properties by 1
        const cube = {
            x: 10,
            y: 10,
            z: 10,
        };


        const sym1 = Symbol('1');
        const sym2 = Symbol('2');
        const sym3 = Symbol('3');
        const sym4 = Symbol('4');
        const object2 = {
            [sym1]: '@@iterator',
            [sym2]: sym3,
        };

        var val = Object.hasOwn(object2, sym1);
        //@ex4:probe : val
        var val = Object.hasOwn(object2, sym2);
        //@ex4:probe : val
        var val = object2[sym1];
        //@ex4:probe : val
        var val = object2[sym2];
        //@ex4:probe : val
        object2['string'] = 'value';
        object2['named_string'] = 'value';
        object2[sym4] = 123;
        var val = Object.hasOwn(object2, 'string')
        //@ex4:probe : val
        var val = Object.hasOwn(object2, 'named_string');
        //@ex4:probe : val
        var val = Object.hasOwn(object2, sym4);
        //@ex4:probe : val
        var val = object2['string'];
        //@ex4:probe : val
        var val = object2[sym4];
        //@ex4:probe : val

    }



    {
        // Verify that normal and nonexistent properties can be deleted.
        const sym = Symbol();
        const obj = { foo: 'bar', [sym]: 'baz' };

        var val = 'foo' in obj;
        //@ex4:probe : val
        var val = sym in obj;
        //@ex4:probe : val
        var val = 'does_not_exist' in obj;
        //@ex4:probe : val
        var val = delete obj['foo'];
        //@ex4:probe : val
        var val = 'foo' in obj;
        //@ex4:probe : val
        var val = sym in obj;
        //@ex4:probe : val
        var val = 'does_not_exist' in obj;
        //@ex4:probe : val
        var val = delete obj[sym];
        //@ex4:probe : val
        var val = 'foo' in obj;
        //@ex4:probe : val
        var val = sym in obj;
        //@ex4:probe : val
        var val = 'does_not_exist' in obj;
        //@ex4:probe : val
    }

    {
        // Verify that non-configurable properties are not deleted.
        const obj = {};

        Object.defineProperty(obj, 'foo', { configurable: false });
        var val = delete obj['foo'];
        //@ex4:probe : val
        var val = 'foo' in obj;
        //@ex4:probe : val
    }

    {
        // Verify that prototype properties are not deleted.
        var Foo = function() {
            this.foo = 'bar';
        }

        Foo.prototype.foo = 'baz';

        const obj = new Foo();

        var val = obj.foo;
        //@ex4:probe : val
        var val = delete obj['foo'];
        //@ex4:probe : val
        var val = obj.foo;
        //@ex4:probe : val
        var val = delete obj['foo'];
        //@ex4:probe : val
        var val = obj.foo;
        //@ex4:probe : val
    }

    {
        // Verify that napi_get_property_names gets the right set of property names,
        // i.e.: includes prototypes, only enumerable properties, skips symbols,
        // and includes indices and converts them to strings.

        const object = {
            __proto__: {
                inherited: 1,
            }
        };

        const fooSymbol = Symbol('foo');

        object.normal = 2;
        object[fooSymbol] = 3;
        Object.defineProperty(object, 'unenumerable', {
            value: 4,
            enumerable: false,
            writable: true,
            configurable: true,
        });
        Object.defineProperty(object, 'writable', {
            value: 4,
            enumerable: true,
            writable: true,
            configurable: false,
        });
        Object.defineProperty(object, 'configurable', {
            value: 4,
            enumerable: true,
            writable: false,
            configurable: true,
        });
        object[5] = 5;

        var val = Object.getOwnPropertyNames(object);
        //@ex4:probe : val

        var val = Object.getOwnPropertySymbols(object);
        //@ex4:probe : val


    }

   
    {
        const obj = { x: 'a', y: 'b', z: 'c' };

        Object.seal(obj);

        var val = Object.isSealed(obj);
        //@ex4:probe : val


        // Sealed objects allow updating existing properties,
        // so this should not throw.
        obj.x = 'd';
    }

    {
        const obj = { x: 10, y: 10, z: 10 };

        Object.freeze(obj);

        var val = Object.isFrozen(obj);
        //@ex4:probe : val


    }
}


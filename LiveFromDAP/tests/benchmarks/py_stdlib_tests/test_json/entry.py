### ORIGINAL TESTS: https://github.com/python/cpython/blob/main/Lib/test/test_json

import decimal
from io import StringIO
from collections import OrderedDict
import json

#@ex1:test_decimal()
def test_decimal():
    rval = json.loads('1.1', parse_float=decimal.Decimal)
    #@ex1: probe : rval

#@ex2:test_float()
def test_float():
    rval = json.loads('1', parse_int=float)
    #@ex1: probe : rval

def test_nonascii_digits_rejected():
    # JSON specifies only ascii digits, see gh-125687
    for num in ["1\uff10", "0.\uff10", "0e\uff10"]:
        with json.assertRaises(json.JSONDecodeError):
            json.loads(num)

#@ex3:test_bytes()
def test_bytes():
    rval = json.loads(b"1")
    #@ex3: probe : rval


#@ex4:test_empty_objects()
def test_empty_objects():
    rval1 = json.loads('{}')
    #@ex4: probe : rval1
    rval2 = json.loads('[]')
    #@ex4: probe : rval2
    rval3 = json.loads('""')
    #@ex4: probe : rval3

#@ex5:test_object_pairs_hook()
def test_object_pairs_hook():
    s = '{"xkd":1, "kcw":2, "art":3, "hxm":4, "qrt":5, "pad":6, "hoy":7}'
    p = [("xkd", 1), ("kcw", 2), ("art", 3), ("hxm", 4),
            ("qrt", 5), ("pad", 6), ("hoy", 7)]
    rvar1 = eval(s)
    rval1 = json.loads(s)
    #@ex5: probe : rvar1
    #@ex5: probe : rval1
    rval2 = json.loads(s, object_pairs_hook=lambda x: x)
    #@ex5: probe : rval2
    rval3 = json.json.load(StringIO(s),
                                    object_pairs_hook=lambda x: x)
    #@ex5: probe : rval3
    od = json.loads(s, object_pairs_hook=OrderedDict)
    pod = OrderedDict(p)
    #@ex5: probe : od
    #@ex5: probe : pod
    # the object_pairs_hook takes priority over the object_hook
    rval4 = json.loads(s, object_pairs_hook=OrderedDict,
                                object_hook=lambda x: None)
    #@ex5: probe : rval4
    # check that empty object literals work (see #17368)
    rval5 = json.loads('{}', object_pairs_hook=OrderedDict)
    #@ex5: probe : rval5
    rval6 = json.loads('{"empty": {}}',
                                object_pairs_hook=OrderedDict)
    #@ex5: probe : rval6

#@ex6:test_decoder_optimizations()
def test_decoder_optimizations():
    # Several optimizations were made that skip over calls to
    # the whitespace regex, so this test is designed to try and
    # exercise the uncommon cases. The array cases are already covered.
    rval = json.loads('{   "key"    :    "value"    ,  "k":"v"    }')
    #@ex6: probe : rval


#@ex7:test_string_with_utf8_bom()
def test_string_with_utf8_bom():
    # see #18958
    # make sure that the BOM is not detected in the middle of a string
    bom = ''.encode('utf-8-sig').decode('utf-8')
    bom_in_str = f'"{bom}"'
    rval1 = json.loads(bom_in_str)
    #@ex7: probe : rval1
    rval2 = json.load(StringIO(bom_in_str))
    #@ex7: probe : rval2

#@ex8:test_default()
def test_default():
        rval1 = json.dumps(type, default=repr)
        #@ex8: probe : rval1
        rval2 = json.dumps(repr(type))
        #@ex8: probe : rval2

#@ex9:test_ordereddict()
def test_ordereddict():
    od = OrderedDict(a=1, b=2, c=3, d=4)
    od.move_to_end('b')
    rval1 = json.dumps(od)
    #@ex9: probe : rval1
    rval2 = json.dumps(od, sort_keys=True)
    #@ex9 : probe : rval2

#@ex10:test_dump()
def test_dump():
    sio = StringIO()
    json.dump({}, sio)
    rval = sio.getvalue()
    #@ex10: probe : rval

#@ex11:test_dumps()
def test_dumps():
    rval = json.dumps({})
    #@ex11: probe : rval

#@ex12:test_dump_skipkeys()
def test_dump_skipkeys():
    v = {b'invalid_key': False, 'valid_key': True}
    s = json.dumps(v, skipkeys=True)
    o = json.loads(s)
    #@ex12: probe : o

#@ex12:test_dump_skipkeys_indent_empty()
def test_dump_skipkeys_indent_empty():
    v = {b'invalid_key': False}
    rval = json.dumps(v, skipkeys=True, indent=4)
    #@ex12: probe : rval

#@ex13:test_skipkeys_indent()
def test_skipkeys_indent():
    v = {b'invalid_key': False, 'valid_key': True}
    rval = json.dumps(v, skipkeys=True, indent=4)
    #@ex13: probe : rval

#@ex14:test_encode_truefalse()
def test_encode_truefalse():
    rval1 = json.dumps(
                {True: False, False: True}, sort_keys=True)
    #@ex14: probe : rval1
    rval2 = json.dumps(
            {2: 3.0, 4.0: 5, False: 1, 6: True}, sort_keys=True)
    #@ex14: probe : rval2

# Issue 16228: Crash on encoding resized list
#@ex15:test_encode_mutated()
def test_encode_mutated():
    a = [object()] * 10
    def crasher(obj):
        del a[-1]
    rval = json.dumps(a, default=crasher)
    #@ex15: probe : rval

# Issue 24094
#@ex16:test_encode_evil_dict()
def test_encode_evil_dict():
    class D(dict):
        def keys(self):
            return L

    class X:
        def __hash__(self):
            del L[0]
            return 1337

        def __lt__(self, o):
            return 0

    L = [X() for i in range(1122)]
    d = D()
    d[1337] = "true.dat"
    rval = json.dumps(d, sort_keys=True)
    #@ex16: probe : rval


CASES = [
    ('/\\"\ucafe\ubabe\uab98\ufcde\ubcda\uef4a\x08\x0c\n\r\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?', '"/\\\\\\"\\ucafe\\ubabe\\uab98\\ufcde\\ubcda\\uef4a\\b\\f\\n\\r\\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?"'),
    ('\u0123\u4567\u89ab\ucdef\uabcd\uef4a', '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"'),
    ('controls', '"controls"'),
    ('\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    ('{"object with 1 member":["array with 1 element"]}', '"{\\"object with 1 member\\":[\\"array with 1 element\\"]}"'),
    (' s p a c e d ', '" s p a c e d "'),
    ('\U0001d120', '"\\ud834\\udd20"'),
    ('\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    ("`1~!@#$%^&*()_+-={':[,]}|;.</>?", '"`1~!@#$%^&*()_+-={\':[,]}|;.</>?"'),
    ('\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    ('\u0123\u4567\u89ab\ucdef\uabcd\uef4a', '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"'),
]

#@ex17:test_encode_basestring_ascii()
def test_encode_basestring_ascii():
    fname = json.encoder.encode_basestring_ascii.__name__
    for input_string, expect in CASES:
        result = json.encoder.encode_basestring_ascii(input_string)
        #@ex17: probe : result

#@ex18:test_ordered_dict()
def test_ordered_dict():
    # See issue 6105
    items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]
    s = json.dumps(OrderedDict(items))
    #@ex18: probe : s

#@ex19:test_sorted_dict()
def test_sorted_dict():
    items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]
    s = json.dumps(dict(items), sort_keys=True)
    #@ex19: probe : s


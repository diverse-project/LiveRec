import unittest
import string
from string import Template
import types




#@ex1:test_attrs()
def test_attrs():
    # While the exact order of the items in these attributes is not
    # technically part of the "language spec", in practice there is almost
    # certainly user code that depends on the order, so de-facto it *is*
    # part of the spec.
    rval1 = string.whitespace
    #@ex1: probe : rval1
    rval2 = string.ascii_lowercase
    #@ex1: probe : rval2
    rval3 = string.ascii_uppercase
    #@ex1: probe : rval3
    rval4 = string.ascii_letters
    #@ex1: probe : rval4
    rval5 = string.digits
    #@ex1: probe : rval5
    rval6 = string.hexdigits
    #@ex1: probe : rval6
    rval7 = string.octdigits
    #@ex1: probe : rval7
    rval8 = string.punctuation
    #@ex1: probe : rval8
    rval9 = string.printable
    #@ex1: probe : rval9

#@ex2:test_capwords()
def test_capwords():
    rval1 = string.capwords('abc def ghi')
    #@ex2: probe : rval1
    rval2 = string.capwords('abc\tdef\nghi')
    #@ex2: probe : rval2
    rval3 = string.capwords('abc\t   def  \nghi')
    #@ex2: probe : rval3
    rval4 = string.capwords('ABC DEF GHI')
    #@ex2: probe : rval4
    rval5 = string.capwords('ABC-DEF-GHI', '-')
    #@ex2: probe : rval5
    rval6 = string.capwords('ABC-def DEF-ghi GHI')
    #@ex2: probe : rval6
    rval7 = string.capwords('   aBc  DeF   ')
    #@ex2: probe : rval7
    rval8 = string.capwords('\taBc\tDeF\t')
    #@ex2: probe : rval8
    rval9 = string.capwords('\taBc\tDeF\t', '\t')
    #@ex2: probe : rval9

#@ex3:test_basic_formatter()
def test_basic_formatter():
    fmt = string.Formatter()
    rval1 = fmt.format("foo")
    #@ex3: probe : rval1
    rval2 = fmt.format("foo{0}", "bar")
    #@ex3: probe : rval2
    rval3 = fmt.format("foo{1}{0}-{1}", "bar", 6)
    #@ex3: probe : rval3

#@ex4:test_format_keyword_arguments()
def test_format_keyword_arguments():
    fmt = string.Formatter()
    rval1 = fmt.format("-{arg}-", arg='test')
    #@ex4: probe : rval1    
    rval2 = fmt.format("-{self}-", self='test')
    #@ex4: probe : rval2    
    rval3 = fmt.format("-{format_string}-", format_string='test')
    #@ex4: probe : rval3


#@ex5:test_auto_numbering()
def test_auto_numbering():
    fmt = string.Formatter()
    rval = fmt.format('foo{}{}', 'bar', 6)
    #@ex5: probe : rval
    rval = fmt.format('foo{1}{num}{1}', None, 'bar', num=6)
    #@ex5: probe : rval
    rval = fmt.format('{:^{}}', 'bar', 6)
    #@ex5: probe : rval
    rval = fmt.format('{:^{}} {}', 'bar', 6, 'X')
    #@ex5: probe : rval
    rval = fmt.format('{:^{pad}}{}', 'foo', 'bar', pad=6)
    #@ex5: probe : rval


#@ex6:test_conversion_specifiers()
def test_conversion_specifiers():
    fmt = string.Formatter()
    rval = fmt.format("-{arg!r}-", arg='test')
    #@ex6: probe : rval
    rval = fmt.format("{0!s}", 'test')
    #@ex6: probe : rval
    # issue13579
    rval = fmt.format("{0!a}", 42)
    #@ex6: probe : rval
    rval = fmt.format("{0!a}",  string.ascii_letters)
    #@ex6: probe : rval
    rval = fmt.format("{0!a}",  chr(255))
    #@ex6: probe : rval
    rval = fmt.format("{0!a}",  chr(256))
    #@ex6: probe : rval

#@ex7:test_name_lookup()
def test_name_lookup():
    fmt = string.Formatter()
    class AnyAttr:
        def __getattr__(self, attr):
            return attr
    x = AnyAttr()
    rval = fmt.format("{0.lumber}{0.jack}", x)
    #@ex7: probe : rval

#@ex8:test_index_lookup()
def test_index_lookup():
    fmt = string.Formatter()
    lookup = ["eggs", "and", "spam"]
    rval = fmt.format("{0[2]}{0[0]}", lookup)
    #@ex8: probe : rval

#@ex9:test_auto_numbering_lookup()
def test_auto_numbering_lookup():
    fmt = string.Formatter()
    namespace = types.SimpleNamespace(foo=types.SimpleNamespace(bar='baz'))
    widths = [None, types.SimpleNamespace(qux=4)]
    rval = fmt.format("{.foo.bar:{[1].qux}}", namespace, widths)
    #@ex9: probe : rval

#@ex10:test_auto_numbering_reenterability()
def test_auto_numbering_reenterability():
    class ReenteringFormatter(string.Formatter):
        def format_field(self, value, format_spec):
            if format_spec.isdigit() and int(format_spec) > 0:
                return self.format('{:{}}!', value, int(format_spec) - 1)
            else:
                return super().format_field(value, format_spec)
    fmt = ReenteringFormatter()
    x = types.SimpleNamespace(a='X')
    rval = fmt.format('{.a:{}}', x, 3)
    #@ex10: probe : rval

#@ex11:test_override_get_value()
def test_override_get_value():
    class NamespaceFormatter(string.Formatter):
        def __init__(self, namespace={}):
            string.Formatter.__init__(self)
            self.namespace = namespace

        def get_value(self, key, args, kwds):
            if isinstance(key, str):
                try:
                    # Check explicitly passed arguments first
                    return kwds[key]
                except KeyError:
                    return self.namespace[key]
            else:
                string.Formatter.get_value(key, args, kwds)

    fmt = NamespaceFormatter({'greeting':'hello'})
    rval = fmt.format("{greeting}, world!")
    #@ex11: probe : rval

#@ex12:test_override_format_field()
def test_override_format_field():
    class CallFormatter(string.Formatter):
        def format_field(self, value, format_spec):
            return format(value(), format_spec)

    fmt = CallFormatter()
    rval = fmt.format('*{0}*', lambda : 'result')
    #@ex12: probe : rval

#@ex13:test_override_convert_field()
def test_override_convert_field():
    class XFormatter(string.Formatter):
        def convert_field(self, value, conversion):
            if conversion == 'x':
                return None
            return super().convert_field(value, conversion)

    fmt = XFormatter()
    rval = fmt.format("{0!r}:{0!x}", 'foo', 'foo')
    #@ex13: probe : rval

#@ex14:test_override_parse()
def test_override_parse():
    class BarFormatter(string.Formatter):
        # returns an iterable that contains tuples of the form:
        # (literal_text, field_name, format_spec, conversion)
        def parse(self, format_string):
            for field in format_string.split('|'):
                if field[0] == '+':
                    # it's markup
                    field_name, _, format_spec = field[1:].partition(':')
                    yield '', field_name, format_spec, None
                else:
                    yield field, None, None, None

    fmt = BarFormatter()
    rval = fmt.format('*|+0:^10s|*', 'foo')
    #@ex14: probe : rval

#@ex15:test_check_unused_args()
def test_check_unused_args():
    class CheckAllUsedFormatter(string.Formatter):
        def check_unused_args(self, used_args, args, kwargs):
            # Track which arguments actually got used
            unused_args = set(kwargs.keys())
            unused_args.update(range(0, len(args)))

            for arg in used_args:
                unused_args.remove(arg)

            if unused_args:
                raise ValueError("unused arguments")

    fmt = CheckAllUsedFormatter()
    rval = fmt.format("{0}", 10)
    #@ex15: probe : rval
    rval = fmt.format("{0}{i}", 10, i=100)
    #@ex15: probe : rval
    rval = fmt.format("{0}{i}{1}", 10, 20, i=100)
    #@ex15: probe : rval


# Template tests (formerly housed in test_pep292.py)

class Bag:
    pass

class Mapping:
    def __getitem__(self, name):
        obj = self
        for part in name.split('.'):
            try:
                obj = getattr(obj, part)
            except AttributeError:
                raise KeyError(name)
        return obj


#@ex16:test_regular_templates()
def test_regular_templates():
    s = Template('$who likes to eat a bag of $what worth $$100')
    rval = s.substitute(dict(who='tim', what='ham'))
    #@ex16: probe : rval

#@ex17:test_regular_templates_with_braces()
def test_regular_templates_with_braces():
    s = Template('$who likes ${what} for ${meal}')
    d = dict(who='tim', what='ham', meal='dinner')
    rval = s.substitute(d)
    #@ex17: probe : rval

#@ex18:test_regular_templates_with_upper_case()
def test_regular_templates_with_upper_case():
    s = Template('$WHO likes ${WHAT} for ${MEAL}')
    d = dict(WHO='tim', WHAT='ham', MEAL='dinner')
    rval = s.substitute(d)
    #@ex18: probe : rval

#@ex19:test_regular_templates_with_non_letters()
def test_regular_templates_with_non_letters():
    s = Template('$_wh0_ likes ${_w_h_a_t_} for ${mea1}')
    d = dict(_wh0_='tim', _w_h_a_t_='ham', mea1='dinner')
    rval = s.substitute(d)
    #@ex19: probe : rval

#@ex20:test_escapes()
def test_escapes():
    s = Template('$who likes to eat a bag of $$what worth $$100')
    rval = s.substitute(dict(who='tim', what='ham'))
    #@ex20: probe : rval
    s = Template('$who likes $$')
    rval = s.substitute(dict(who='tim', what='ham'))
    #@ex20: probe : rval

#@ex21:test_percents()
def test_percents():
    s = Template('%(foo)s $foo ${foo}')
    d = dict(foo='baz')
    rval = s.substitute(d)
    #@ex21: probe : rval
    rval = s.safe_substitute(d)
    #@ex21: probe : rval

#@ex22:test_stringification()
def test_stringification():
    s = Template('tim has eaten $count bags of ham today')
    d = dict(count=7)
    rval = s.substitute(d)
    #@ex22: probe : rval
    rval = s.safe_substitute(d)
    #@ex22: probe : rval
    s = Template('tim has eaten ${count} bags of ham today')
    rval = s.substitute(d)
    #@ex22: probe : rval

#@ex23:test_tupleargs()
def test_tupleargs():
    s = Template('$who ate ${meal}')
    d = dict(who=('tim', 'fred'), meal=('ham', 'kung pao'))
    rval = s.substitute(d)
    #@ex23: probe : rval
    rval = s.safe_substitute(d)
    #@ex23: probe : rval

#@ex24:test_SafeTemplate()
def test_SafeTemplate():
    s = Template('$who likes ${what} for ${meal}')
    rval = s.safe_substitute(dict(who='tim'))
    #@ex24: probe : rval
    rval = s.safe_substitute(dict(what='ham'))
    #@ex24: probe : rval
    rval = s.safe_substitute(dict(what='ham', meal='dinner'))
    #@ex24: probe : rval
    rval = s.safe_substitute(dict(who='tim', what='ham'))
    #@ex24: probe : rval
    rval = s.safe_substitute(dict(who='tim', what='ham', meal='dinner'))
    #@ex24: probe : rval

#@ex25:test_idpattern_override()
def test_idpattern_override():
    class PathPattern(Template):
        idpattern = r'[_a-z][._a-z0-9]*'
    m = Mapping()
    m.bag = Bag()
    m.bag.foo = Bag()
    m.bag.foo.who = 'tim'
    m.bag.what = 'ham'
    s = PathPattern('$bag.foo.who likes to eat a bag of $bag.what')
    rval = s.substitute(m)
    #@ex25: probe : rval

#@ex26:test_flags_override()
def test_flags_override():
    class MyPattern(Template):
        flags = 0
    s = MyPattern('$wHO likes ${WHAT} for ${meal}')
    d = dict(wHO='tim', WHAT='ham', meal='dinner', w='fred')
    rval = s.safe_substitute(d)
    #@ex26: probe : rval

#@ex27:test_idpattern_override_inside_outside()
def test_idpattern_override_inside_outside():
    # bpo-1198569: Allow the regexp inside and outside braces to be
    # different when deriving from Template.
    class MyPattern(Template):
        idpattern = r'[a-z]+'
        braceidpattern = r'[A-Z]+'
        flags = 0
    m = dict(foo='foo', BAR='BAR')
    s = MyPattern('$foo ${BAR}')
    rval = s.substitute(m)
    #@ex27: probe : rval

#@ex28:test_pattern_override()
def test_pattern_override():
    class MyPattern(Template):
        pattern = r"""
        (?P<escaped>@{2})                   |
        @(?P<named>[_a-z][._a-z0-9]*)       |
        @{(?P<braced>[_a-z][._a-z0-9]*)}    |
        (?P<invalid>@)
        """
    m = Mapping()
    m.bag = Bag()
    m.bag.foo = Bag()
    m.bag.foo.who = 'tim'
    m.bag.what = 'ham'
    s = MyPattern('@bag.foo.who likes to eat a bag of @bag.what')
    rval = s.substitute(m)
    #@ex28: probe : rval

#@ex29:test_braced_override()
def test_braced_override():
    class MyTemplate(Template):
        pattern = r"""
        \$(?:
            (?P<escaped>$)                     |
            (?P<named>[_a-z][_a-z0-9]*)        |
            @@(?P<braced>[_a-z][_a-z0-9]*)@@   |
            (?P<invalid>)                      |
        )
        """

    tmpl = 'PyCon in $@@location@@'
    t = MyTemplate(tmpl)
    val = t.substitute({'location': 'Cleveland'})
    #@ex29: probe : val

#@ex30:test_braced_override_safe()
def test_braced_override_safe():
    class MyTemplate(Template):
        pattern = r"""
        \$(?:
            (?P<escaped>$)                     |
            (?P<named>[_a-z][_a-z0-9]*)        |
            @@(?P<braced>[_a-z][_a-z0-9]*)@@   |
            (?P<invalid>)                      |
        )
        """

    tmpl = 'PyCon in $@@location@@'
    t = MyTemplate(tmpl)
    rval = t.safe_substitute()
    #@ex30: probe : rval
    val = t.safe_substitute({'location': 'Cleveland'})
    #@ex30: probe : val

#@ex31:test_unicode_values()
def test_unicode_values():
    s = Template('$who likes $what')
    d = dict(who='t\xffm', what='f\xfe\fed')
    rval = s.substitute(d)
    #@ex31: probe : rval

#@ex32:test_keyword_arguments()
def test_keyword_arguments():
    s = Template('$who likes $what')
    rval = s.substitute(who='tim', what='ham')
    #@ex32: probe : rval
    rval = s.substitute(dict(who='tim'), what='ham')
    #@ex32: probe : rval
    s.substitute(dict(who='fred', what='kung pao'),
                    who='tim', what='ham')
    #@ex32: probe : rval
    s = Template('the mapping is $mapping')
    s.substitute(dict(foo='none'), mapping='bozo')
    #@ex32: probe : rval
    rval = s.substitute(dict(mapping='one'), mapping='two')
    #@ex32: probe : rval

    s = Template('the self is $self')
    rval = s.substitute(self='bozo')
    #@ex32: probe : rval

#@ex33:test_keyword_arguments_safe()
def test_keyword_arguments_safe():
    s = Template('$who likes $what')
    rval = s.safe_substitute(who='tim', what='ham')
    #@ex33: probe : rval
    rval = s.safe_substitute(dict(who='tim'), what='ham')
    #@ex33: probe : rval
    rval = s.safe_substitute(dict(who='fred', what='kung pao'),
                    who='tim', what='ham')
    #@ex33: probe : rval
    s = Template('the mapping is $mapping')
    rval = s.safe_substitute(dict(foo='none'), mapping='bozo')
    #@ex33: probe : rval
    rval = s.safe_substitute(dict(mapping='one'), mapping='two')
    #@ex33: probe : rval

    s = Template('the self is $self')
    rval = s.safe_substitute(self='bozo')
    #@ex33: probe : rval

#@ex34:test_delimiter_override()
def test_delimiter_override():
    class AmpersandTemplate(Template):
        delimiter = '&'
    s = AmpersandTemplate('this &gift is for &{who} &&')
    rval = s.substitute(gift='bud', who='you')
    #@ex34: probe : rval
    rval = s.safe_substitute(gift='bud', who='you')
    #@ex34: probe : rval
    rval = s.safe_substitute()
    #@ex34: probe : rval
    s = AmpersandTemplate('this &gift is for &{who} &')
    rval = s.safe_substitute()
    #@ex34: probe : rval
    class PieDelims(Template):
        delimiter = '@'
    s = PieDelims('@who likes to eat a bag of @{what} worth $100')
    rval = s.substitute(dict(who='tim', what='ham'))
    #@ex34: probe : rval

#@ex35:test_get_identifiers()
def test_get_identifiers():
    s = Template('$who likes to eat a bag of ${what} worth $$100')
    ids = s.get_identifiers()
    #@ex35: probe : ids

    # repeated identifiers only included once
    s = Template('$who likes to eat a bag of ${what} worth $$100; ${who} likes to eat a bag of $what worth $$100')
    ids = s.get_identifiers()
    #@ex35: probe : ids

    # invalid identifiers are ignored
    s = Template('$who likes to eat a bag of ${what} worth $100')
    ids = s.get_identifiers()
    #@ex35: probe : ids



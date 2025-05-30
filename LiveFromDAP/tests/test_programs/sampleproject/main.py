# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package


import unittest



from src.sample.simple import add_one
from tests.test_simple import TestSimple


#@ex1:test_add_one()
def test_add_one():
    res = add_one(5)
    #@ex1: probe : res

test = TestSimple()
test.test_add_one()

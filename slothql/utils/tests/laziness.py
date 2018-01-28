import pytest

from ..laziness import LazyInitMixin


class ExceptionTest(Exception):
    pass


class Class(LazyInitMixin):
    def __init__(self, a, b):
        print('init')
        self.a = a
        self.b = b
        raise ExceptionTest


def test_lazy_init_getattr():
    a = Class('foo', b='bar')
    with pytest.raises(ExceptionTest):
        hasattr(a, 'a')
    assert 'foo' is a.a
    assert 'bar' is a.b


def test_lazy_init_setattr():
    a = Class('foo', b='bar')
    print('after init')
    with pytest.raises(ExceptionTest):
        a.c = 'not baz'  # isn't being fully executed, as an exception occurs first in __init__
    a.c = 'baz'
    assert 'foo' is a.a
    assert 'bar' is a.b
    assert 'baz' is a.c

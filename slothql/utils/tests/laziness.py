import pytest

from ..laziness import LazyInitMixin


class Executed(Exception):
    pass


class Class(LazyInitMixin):
    def __init__(self, a='foo', b='bar'):
        self.a = a
        self.b = b
        raise Executed


def test_lazy_init_getattr():
    a = Class()
    with pytest.raises(Executed):
        hasattr(a, 'a')
    assert 'foo' is a.a
    assert 'bar' is a.b


def test_lazy_init_setattr():
    a = Class()
    with pytest.raises(Executed):
        a.c = 'not baz'  # isn't being fully executed, as an exception occurs first in __init__
    a.c = 'baz'
    assert 'foo' is a.a
    assert 'bar' is a.b
    assert 'baz' is a.c


def test_lazy_init_isinstance():
    assert isinstance(Class(), Class)


def test_lazy_init_type():
    """
    type() behaviour cannot be modified
    """
    assert type(Class()) is not Class

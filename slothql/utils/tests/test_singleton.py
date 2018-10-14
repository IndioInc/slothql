import copy

from ..singleton import Singleton


def test_new():
    class Foo(metaclass=Singleton):
        pass

    assert id(Foo()) == id(Foo())


def test_copy():
    class Foo(metaclass=Singleton):
        pass

    assert Foo() == copy.copy(Foo())

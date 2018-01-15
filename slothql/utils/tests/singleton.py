from ..singleton import Singleton


def test_singleton():
    class Foo(metaclass=Singleton):
        pass

    assert id(Foo()) == id(Foo())

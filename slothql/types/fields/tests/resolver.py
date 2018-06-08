import pytest

from ..resolver import PartialResolver, get_resolver


class A:
    def method1(self):
        return "foo"

    def method2(self, obj):
        return "foo"

    def method3(self, obj, info):
        return "foo"

    @staticmethod
    def static1():
        return "foo"

    @staticmethod
    def static2(obj):
        return "foo"

    @staticmethod
    def static3(obj, info):
        return "foo"

    @classmethod
    def class1(cls):
        return "foo"

    @classmethod
    def class2(cls, obj):
        return "foo"

    @classmethod
    def class3(cls, obj, info):
        return "foo"


@pytest.mark.parametrize(
    "resolver",
    (
        lambda: "foo",
        lambda parent: "foo",
        lambda parent, info: "foo",
        lambda parent, info, args: "foo",
        A.method1,
        A.method2,
        A.method3,
        A.static1,
        A.static2,
        A.static3,
        A.class1,
        A.class2,
        A.class3,
    ),
)
def test_resolve(resolver: PartialResolver, field_mock):
    assert "foo" == get_resolver(field_mock, resolver)(None, None, None)

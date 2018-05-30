import collections

import pytest

import slothql
from slothql.types import scalars


@pytest.mark.incremental
class TestField:
    def test_can_init(self, type_mock):
        slothql.Field(of_type=type_mock())

    def test_has_resolver_callable(self, type_mock):
        assert callable(slothql.Field(of_type=type_mock()).resolver)

    def test_no_resolver(self, type_mock, info_mock):
        field = slothql.Field(of_type=type_mock())
        assert field.resolver(None, info_mock()) is None

    def test_default_resolver(self, type_mock, info_mock):
        of_type = type_mock()
        field = slothql.Field(of_type=of_type)
        assert 1 == field.resolve(None, {'a': 1}, info_mock(field_name='a'))


@pytest.mark.parametrize('obj, expected', (
        ({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': None}),
        (collections.namedtuple('A', ('a', 'b'))(1, 2), {'a': 1, 'b': 2, 'c': None}),
        (None, {'a': None}),
        ({'a': {'nested': 'hell yeah'}}, {'a': {'nested': 'hell yeah'}}),
))
def test_resolve_field(obj, expected, info_mock, type_mock):
    for field_name, expected_value in expected.items():
        assert expected_value == slothql.Field(type_mock()).resolve_field(obj, info_mock(field_name=field_name), {})


def test_field_name(type_mock):
    class Foo(slothql.Object):
        field = slothql.Field(type_mock)

    assert 'field' == Foo.field.name


def test_field_no_parent():
    assert None is slothql.Field('self').parent


def test_field_parent():
    class Foo(slothql.Object):
        bar = slothql.Field('self')

    assert Foo == Foo.bar.parent == Foo.bar.of_type


@pytest.mark.xfail
def test_field_comparison_different_type(type_mock):
    assert slothql.Field(scalars.StringType) != slothql.Field(scalars.BooleanType)


def test_field_comparison_same_type(type_mock):
    assert slothql.Field(slothql.BaseType) == slothql.Field(slothql.BaseType)


def test_field_comparison_not_field(type_mock):
    with pytest.raises(ValueError) as exc_info:
        slothql.Field(type_mock()) != type_mock()
    assert 'slothql.Field can only be compared with other slothql.Field instances,' \
           ' not <class \'slothql.types.base.BaseType\'>' == str(exc_info.value)

import collections
from functools import partial

import pytest

from ..field import Field


@pytest.mark.incremental
class TestField:
    def test_can_init(self, type_mock):
        Field(of_type=type_mock())

    def test_has_resolver_callable(self, type_mock):
        assert callable(Field(of_type=type_mock()).resolver)

    def test_no_resolver(self, type_mock, info_mock):
        field = Field(of_type=type_mock())
        assert field.resolver(None, info_mock()) is None

    def test_default_resolver(self, type_mock, partials_equal):
        of_type = type_mock()
        field = Field(of_type=of_type)
        assert partials_equal(partial(field.resolve, field.get_default_resolver(of_type)), field.resolver)


@pytest.mark.parametrize('obj, expected', (
        ({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': None}),
        (collections.namedtuple('A', ('a', 'b'))(1, 2), {'a': 1, 'b': 2, 'c': None}),
        (None, {'a': None}),
        ({'a': {'nested': 'hell yeah'}}, {'a': {'nested': 'hell yeah'}}),
))
def test_resolve_field(obj, expected, info_mock, type_mock):
    for field_name, expected_value in expected.items():
        assert expected_value == Field(type_mock()).resolve_field(obj, info_mock(field_name=field_name), {})

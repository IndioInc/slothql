import collections
from functools import partial

import pytest
from unittest import mock

from graphql.type.definition import GraphQLType

from ..field import Field


@pytest.mark.incremental
class TestField:
    def test_can_init(self, type):
        Field(of_type=type())

    def test_has_resolver_callable(self, type):
        assert callable(Field(of_type=type()).resolver)

    def test_no_resolver(self, type, info):
        field = Field(of_type=type())
        assert field.resolver(None, info()) is None

    def test_default_resolver(self, partials_equal):
        field = Field(of_type=mock.Mock(spec=GraphQLType))
        assert partials_equal(partial(field.resolve, field.default_resolver), field.resolver)


@pytest.mark.parametrize("obj, expected", (
        ({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': None}),
        (collections.namedtuple('A', ('a', 'b'))(1, 2), {'a': 1, 'b': 2, 'c': None}),
        (None, {'a': None}),
        ({'a': {'nested': 'hell yeah'}}, {'a': {'nested': 'hell yeah'}}),
))
def test_resolve_field(obj, expected, info):
    for field_name, expected_value in expected.items():
        assert expected_value == Field.resolve_field(obj, info(field_name=field_name))

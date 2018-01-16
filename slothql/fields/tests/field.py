import collections
import pytest
from unittest import mock

import graphql
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

    def test_default_resolver(self, type, info):
        field = Field(of_type=type())
        assert 'bar' == field.resolver({'foo': 'bar'}, info(field_name='foo'))

    def test_resolver_resolution(self, resolver):
        field = Field(of_type=mock.Mock(spec=GraphQLType), resolver=resolver)
        with mock.patch.object(Field, 'resolve_field') as resolve_field:
            field.resolver('object', mock.Mock(spec=graphql.ResolveInfo, field_name='field'))
        resolve_field.assert_called_with('object', 'field')


@pytest.mark.parametrize("obj, expected", (
        ({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': None}),
        (collections.namedtuple('A', ('a', 'b'))(1, 2), {'a': 1, 'b': 2, 'c': None}),
))
def test_resolve_field(obj, expected):
    for field_name, expected_value in expected.items():
        assert expected_value == Field.resolve_field(obj, field_name)

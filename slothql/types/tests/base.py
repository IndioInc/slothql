import pytest

import graphql

from slothql.types.base import BaseType


@pytest.mark.parametrize('type_name, expected_name', (
        ('Foo', 'Foo'),
        (None, 'FooType'),
))
def test_meta_name(type_name, expected_name):
    class FooType(BaseType):
        def __init__(self):
            super().__init__(graphql.GraphQLString)

        class Meta:
            name = type_name

    assert expected_name == FooType()._meta.name

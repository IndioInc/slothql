import graphql

from slothql.types.base import BaseType


def test_meta_description():
    class TestType(BaseType):
        def __init__(self):
            super().__init__(graphql.GraphQLString)

        class Meta:
            description = 'foo'

    # assert 'foo' == TestType._meta.description == TestType()._type.description != graphql.GraphQLString.description

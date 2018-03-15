import pytest

import graphql
from typing import Type

import slothql

from .. import scalars


@pytest.mark.parametrize('scalar_type, name, value', (
        (scalars.IntegerType, 'name', 'Integer'),
        (scalars.IntegerType, 'description', graphql.GraphQLInt.description),
        (scalars.FloatType, 'name', 'Float'),
        (scalars.FloatType, 'description', graphql.GraphQLFloat.description),
        (scalars.StringType, 'name', 'String'),
        (scalars.StringType, 'description', graphql.GraphQLString.description),
        (scalars.BooleanType, 'description', graphql.GraphQLBoolean.description),
        (scalars.BooleanType, 'name', 'Boolean'),
        (scalars.IDType, 'name', 'ID'),
        (scalars.IDType, 'description', graphql.GraphQLID.description),
))
def test_scalar_type_props(scalar_type, name, value):
    assert value == getattr(scalar_type()._meta, name)


def test_scalar_integration():
    class Foo(slothql.Object):
        integer = slothql.Integer()
        boolean = slothql.Boolean()
        float = slothql.Float()
        id = slothql.ID()
        string = slothql.String()

    data = {'integer': 12, 'boolean': True, 'float': 12.34, 'id': 'guid', 'string': 'foo bar'}

    class Query(slothql.Object):
        foo = slothql.Field(Foo, resolver=lambda: data)

    schema = slothql.Schema(query=Query)

    assert {'data': {'foo': data}} == slothql.gql(schema, 'query { foo { integer boolean float id string } }')


@pytest.mark.parametrize('scalar_type, value, expected', (
        (scalars.IntegerType, 1, 1),
        (scalars.IntegerType, 0, 0),
        (scalars.IntegerType, -1, -1),
        (scalars.IntegerType, None, None),

        (scalars.FloatType, 1.0, 1.0),
        (scalars.FloatType, 0.0, 0.0),
        (scalars.FloatType, -1.0, -1.0),
        (scalars.FloatType, 1.1, 1.1),
        (scalars.FloatType, 0.1, 0.1),
        (scalars.FloatType, -1.1, -1.1),
        (scalars.FloatType, None, None),

        (scalars.StringType, 'string', 'string'),
        (scalars.StringType, u'\U0001F601', u'\U0001F601'),
        (scalars.StringType, None, None),

        (scalars.BooleanType, True, True),
        (scalars.BooleanType, False, False),
        (scalars.BooleanType, None, None),

        (scalars.IDType, '1', '1'),
        (scalars.IDType, 1, 1),
        (scalars.IDType, None, None),
))
def test_serialize(scalar_type: Type[scalars.ScalarType], value, expected):
    serialized = scalar_type.serialize(value)
    assert expected == serialized and type(expected) is type(serialized)


@pytest.mark.parametrize('scalar_type, value', (
        (scalars.IntegerType, 0.1),
        (scalars.IntegerType, '1'),
        (scalars.IntegerType, True),
        (scalars.IntegerType, False),
        (scalars.IntegerType, 2 ** 53),
        (scalars.IntegerType, -(2 ** 53)),

        (scalars.FloatType, '1.0'),
        (scalars.FloatType, True),
        (scalars.FloatType, False),

        (scalars.StringType, 1),
        (scalars.StringType, True),
        (scalars.StringType, False),
        (scalars.StringType, 1),

        (scalars.BooleanType, 'true'),
        (scalars.BooleanType, ''),
        (scalars.BooleanType, 1),
        (scalars.BooleanType, 0),

        (scalars.IDType, 0.1),
        (scalars.IDType, 2 ** 53),
        (scalars.IDType, -(2 ** 53)),
        (scalars.IDType, True),
        (scalars.IDType, False),
))
def test_serialize__invalid(scalar_type: Type[scalars.ScalarType], value):
    with pytest.raises(ValueError) as exc_info:
        scalar_type.serialize(value)
    assert f'`{scalar_type.__name__}.serialize` received invalid value {repr(value)}' == str(exc_info.value)

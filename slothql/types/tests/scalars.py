import pytest

import graphql

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


@pytest.mark.xfail
def test_serialize():
    pass


@pytest.mark.xfail
def test_parse():
    pass

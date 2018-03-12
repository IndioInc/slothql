import pytest

import graphql

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


@pytest.mark.xfail
def test_serialize():
    pass


@pytest.mark.xfail
def test_parse():
    pass

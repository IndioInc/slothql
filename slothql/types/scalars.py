from graphql.type import scalars

from .base import BaseType


class ScalarType(BaseType):
    @classmethod
    def serialize(cls, value):
        return value


class IntegerType(ScalarType):
    class Meta:
        name = 'Integer'
        description = scalars.GraphQLInt.description


class FloatType(ScalarType):
    class Meta:
        name = 'Float'
        description = scalars.GraphQLFloat.description


class StringType(ScalarType):
    class Meta:
        name = 'String'
        description = scalars.GraphQLString.description


class BooleanType(ScalarType):
    class Meta:
        name = 'Boolean'
        description = scalars.GraphQLBoolean.description


class IDType(ScalarType):
    class Meta:
        name = 'ID'
        description = scalars.GraphQLID.description


def patch_default_scalar(scalar_type: ScalarType, graphql_type: scalars.GraphQLScalarType):
    graphql_type.name = scalar_type._meta.name
    graphql_type.description = scalar_type._meta.description
    graphql_type.serialize = scalar_type.serialize


patch_default_scalar(IntegerType(), scalars.GraphQLInt)
patch_default_scalar(FloatType(), scalars.GraphQLFloat)
patch_default_scalar(StringType(), scalars.GraphQLString)
patch_default_scalar(BooleanType(), scalars.GraphQLBoolean)
patch_default_scalar(IDType(), scalars.GraphQLID)

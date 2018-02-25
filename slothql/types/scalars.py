import graphql
from graphql.type import scalars

from .base import BaseType


class ScalarType(BaseType):
    def __init__(self):
        super().__init__(graphql.GraphQLScalarType(
            name=self._meta.name,
            description=self._meta.description,
            serialize=self.serialize,
            parse_value=self.serialize,  # FIXME: noqa
            parse_literal=self.serialize,  # FIXME: noqa
        ))

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
    type_ = scalar_type._type
    scalar_type._type = graphql_type
    scalar_type._type.name = type_.name
    scalar_type._type.description = type_.description
    scalar_type._type.serialize = type_.serialize
    scalar_type._type.parse_value = type_.parse_value
    scalar_type._type.parse_literal = type_.parse_literal


patch_default_scalar(IntegerType(), scalars.GraphQLInt)
patch_default_scalar(FloatType(), scalars.GraphQLFloat)
patch_default_scalar(StringType(), scalars.GraphQLString)
patch_default_scalar(BooleanType(), scalars.GraphQLBoolean)
patch_default_scalar(IDType(), scalars.GraphQLID)

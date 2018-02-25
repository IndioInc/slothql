import graphql
from graphql.type import scalars

from .base import BaseType


class ScalarType(BaseType):
    def __init__(self):
        super().__init__(graphql.GraphQLScalarType(
            name=self._meta.name,
            description=self._meta.description,
            serialize=self.serialize,
            parse_value=self.deserialize,
            parse_literal=self.parse_literal,
        ))

    @classmethod
    def serialize(cls, value):
        return value

    @classmethod
    def deserialize(cls, value):
        return value

    @classmethod
    def parse_literal(cls, ast):
        raise NotImplementedError


class IntegerType(ScalarType):
    class Meta:
        name = 'Integer'
        description = scalars.GraphQLInt.description

    @classmethod
    def parse_literal(cls, ast):
        return scalars.parse_int_literal(ast)


class FloatType(ScalarType):
    class Meta:
        name = 'Float'
        description = scalars.GraphQLFloat.description

    @classmethod
    def parse_literal(cls, ast):
        return scalars.parse_float_literal(ast)


class StringType(ScalarType):
    class Meta:
        name = 'String'
        description = scalars.GraphQLString.description

    @classmethod
    def parse_literal(cls, ast):
        return scalars.parse_string_literal(ast)


class BooleanType(ScalarType):
    class Meta:
        name = 'Boolean'
        description = scalars.GraphQLBoolean.description

    @classmethod
    def parse_literal(cls, ast):
        return scalars.parse_boolean_literal(ast)


class IDType(ScalarType):
    class Meta:
        name = 'ID'
        description = scalars.GraphQLID.description

    @classmethod
    def parse_literal(cls, ast):
        return scalars.parse_float_literal(ast)


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

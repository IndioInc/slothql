import typing as t

from graphql.type import scalars

from .base import BaseType


class ScalarType(BaseType):
    @classmethod
    def serialize(cls, value):
        raise NotImplementedError


MAX_SAFE_INTEGER = 2 ** 53 - 1
MIN_SAFE_INTEGER = -MAX_SAFE_INTEGER


class IntegerType(ScalarType):
    class Meta:
        name = 'Integer'
        description = scalars.GraphQLInt.description

    @classmethod
    def serialize(cls, value) -> t.Optional[int]:
        if value is None:
            return None
        if isinstance(value, int) and not isinstance(value, bool):
            if MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
                return value
        raise TypeError(f'`{cls.__name__}.serialize` received invalid value {repr(value)}')


class FloatType(ScalarType):
    class Meta:
        name = 'Float'
        description = scalars.GraphQLFloat.description

    @classmethod
    def serialize(cls, value) -> t.Optional[float]:
        if value is None or isinstance(value, float):
            return value
        raise TypeError(f'`{cls.__name__}.serialize` received invalid value {repr(value)}')


class StringType(ScalarType):
    class Meta:
        name = 'String'
        description = scalars.GraphQLString.description

    @classmethod
    def serialize(cls, value) -> t.Optional[str]:
        if value is None or isinstance(value, str):
            return value
        raise TypeError(f'`{cls.__name__}.serialize` received invalid value {repr(value)}')


class BooleanType(ScalarType):
    class Meta:
        name = 'Boolean'
        description = scalars.GraphQLBoolean.description

    @classmethod
    def serialize(cls, value) -> t.Optional[bool]:
        if value is None or isinstance(value, bool):
            return value
        raise TypeError(f'`{cls.__name__}.serialize` received invalid value {repr(value)}')


class IDType(ScalarType):
    class Meta:
        name = 'ID'
        description = scalars.GraphQLID.description

    @classmethod
    def serialize(cls, value) -> t.Union[int, str]:
        if value is None or isinstance(value, str):
            return value
        try:
            return IntegerType.serialize(value)
        except TypeError:
            raise TypeError(f'`{cls.__name__}.serialize` received invalid value {repr(value)}')


def patch_default_scalar(scalar_type: t.Type[ScalarType], graphql_type: scalars.GraphQLScalarType):
    graphql_type.name = scalar_type._meta.name
    graphql_type.description = scalar_type._meta.description
    graphql_type.serialize = scalar_type.serialize


patch_default_scalar(IntegerType, scalars.GraphQLInt)
patch_default_scalar(FloatType, scalars.GraphQLFloat)
patch_default_scalar(StringType, scalars.GraphQLString)
patch_default_scalar(BooleanType, scalars.GraphQLBoolean)
patch_default_scalar(IDType, scalars.GraphQLID)

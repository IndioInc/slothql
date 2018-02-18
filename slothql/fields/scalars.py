import graphql

from slothql.base import BaseType
from .field import Field


class Scalar(Field):
    @classmethod
    def resolve(cls, resolver, parent, info: graphql.ResolveInfo):
        return cls.serialize(super().resolve(resolver, parent, info))

    @classmethod
    def serialize(cls, value):
        return value


class BooleanType(BaseType):
    def __init__(self):
        super().__init__(graphql.GraphQLBoolean)


class Boolean(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=BooleanType, **kwargs)


class IntegerType(BaseType):
    def __init__(self):
        super().__init__(graphql.GraphQLInt)


class Integer(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=IntegerType, **kwargs)


class FloatType(BaseType):
    def __init__(self):
        super().__init__(graphql.GraphQLFloat)


class Float(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=FloatType, **kwargs)


class StringType(BaseType):
    def __init__(self):
        super().__init__(graphql.GraphQLString)


class String(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=StringType, **kwargs)


class JSONString(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=StringType, **kwargs)


class IDType(BaseType):
    def __init__(self):
        super().__init__(graphql.GraphQLID)


class ID(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=IDType, **kwargs)

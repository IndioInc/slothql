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


class Boolean(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=BaseType(graphql.GraphQLBoolean), **kwargs)


class Integer(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=BaseType(graphql.GraphQLInt), **kwargs)


class Float(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=BaseType(graphql.GraphQLFloat), **kwargs)


class String(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=BaseType(graphql.GraphQLString), **kwargs)


class JSONString(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=BaseType(graphql.GraphQLString), **kwargs)


class ID(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=BaseType(graphql.GraphQLID), **kwargs)

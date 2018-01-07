import graphql

from .field import Field


class Scalar(Field):
    @classmethod
    def resolve(cls, resolver, parent, info: graphql.ResolveInfo):
        return cls.serialize(super().resolve(resolver, parent, info))

    @classmethod
    def serialize(cls, value):
        return value


class String(Scalar):
    def __init__(self, resolver=None):
        super().__init__(of_type=graphql.GraphQLString, resolver=resolver)

    @classmethod
    def serialize(cls, value):
        return str(value)

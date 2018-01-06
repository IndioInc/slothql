import graphql

from .field import Field


class ScalarField(Field):
    @classmethod
    def resolve(cls, resolver, parent, info: graphql.ResolveInfo, *args, **kwargs):
        return cls.serialize(parent)

    @classmethod
    def serialize(cls, value):
        return value


class StringField(ScalarField):
    def __init__(self, **kwargs):
        super().__init__(of_type=graphql.GraphQLString)

    @classmethod
    def serialize(cls, value):
        return str(value)

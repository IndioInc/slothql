import graphql

from .field import Field


class Scalar(Field):
    @classmethod
    def resolve(cls, resolver, parent, info: graphql.ResolveInfo):
        return cls.serialize(super().resolve(resolver, parent, info))

    @classmethod
    def serialize(cls, value):
        return value


class Boolean(Scalar):
    def __init__(self, resolver=None):
        super().__init__(of_type=graphql.GraphQLBoolean, resolver=resolver)


class Integer(Scalar):
    def __init__(self, resolver=None):
        super().__init__(of_type=graphql.GraphQLInt, resolver=resolver)


class Float(Scalar):
    def __init__(self, resolver=None):
        super().__init__(of_type=graphql.GraphQLFloat, resolver=resolver)


class String(Scalar):
    def __init__(self, resolver=None):
        super().__init__(of_type=graphql.GraphQLString, resolver=resolver)


class JSONString(Scalar):
    def __init__(self, resolver=None):
        super().__init__(of_type=graphql.GraphQLString, resolver=resolver)


class ID(Scalar):
    def __init__(self, resolver=None):
        super().__init__(of_type=graphql.GraphQLID, resolver=resolver)


# Shortcuts
Bool = Boolean
Int = Integer
Str = String

import graphql

from .. import scalars
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
        super().__init__(of_type=scalars.BooleanType, **kwargs)


class Integer(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.IntegerType, **kwargs)


class Float(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.FloatType, **kwargs)


class String(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.StringType, **kwargs)


class JSONString(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.StringType, **kwargs)


class ID(Scalar):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.IDType, **kwargs)

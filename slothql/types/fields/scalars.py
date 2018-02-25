import graphql

from .. import scalars
from .field import Field


class SerializableMixin(Field):
    @classmethod
    def resolve(cls, resolver, parent, info: graphql.ResolveInfo):
        return cls.serialize(super().resolve(resolver, parent, info))

    @classmethod
    def serialize(cls, value):
        return value


class Boolean(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.BooleanType, **kwargs)


class Integer(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.IntegerType, **kwargs)


class Float(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.FloatType, **kwargs)


class String(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.StringType, **kwargs)


class JSONString(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.StringType, **kwargs)


class ID(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=scalars.IDType, **kwargs)

import functools

import graphql

from slothql.utils import LazyInitMixin
from slothql.base import LazyType, resolve_lazy_type, BaseType
from .list import ListMixin
from .resolver import Resolver


class Field(LazyInitMixin, ListMixin, graphql.GraphQLField):
    __slots__ = ()

    def get_default_resolver(self, of_type):
        from slothql import types
        if isinstance(of_type, types.Object):
            return lambda obj, info: of_type.resolve(self.resolve_field(obj, info), info)
        return self.resolve_field

    def get_resolver(self, resolver, of_type: BaseType):
        return Resolver(self, resolver).func or self.get_default_resolver(of_type)

    def __init__(self, of_type: LazyType, resolver=None, source: str = None, **kwargs):
        of_type = resolve_lazy_type(of_type)
        resolver = self.get_resolver(resolver, of_type)
        assert callable(resolver), f'resolver needs to be callable, not {resolver}'

        assert source is None or isinstance(source, str), f'source= has to be of type str'
        self.source = source

        super().__init__(type=of_type._type, resolver=functools.partial(self.resolve, resolver), **kwargs)

    @classmethod
    def resolve(cls, resolver, obj, info: graphql.ResolveInfo):
        return resolver(obj, info)

    def __repr__(self) -> str:
        return f'<Field: {repr(self.type)}>'

    def get_internal_name(self, name: str) -> str:
        return self.source or name

    def resolve_field(self, obj, info: graphql.ResolveInfo):
        if obj is None:
            return None
        name = self.get_internal_name(info.field_name)
        if isinstance(obj, dict):
            value = obj.get(name)
        else:
            value = getattr(obj, name, None)
        return value

import functools

import graphql

from slothql.utils import LazyInitMixin
from slothql import types
from slothql.types.base import LazyType, resolve_lazy_type, BaseType

from .mixins import ListMixin
from .resolver import get_resolver, Resolver, PartialResolver, ResolveArgs


class Field(LazyInitMixin, ListMixin, graphql.GraphQLField):
    __slots__ = ()

    def get_default_resolver(self, of_type: BaseType) -> Resolver:
        if isinstance(of_type, types.Object):
            return lambda obj, info, args: of_type.resolve(self.resolve_field(obj, info, args), info, args)
        return self.resolve_field

    def get_resolver(self, resolver: PartialResolver, of_type: BaseType) -> Resolver:
        return get_resolver(self, resolver) or self.get_default_resolver(of_type)

    def __init__(self, of_type: LazyType, resolver: PartialResolver = None, source: str = None, **kwargs):
        of_type = resolve_lazy_type(of_type)
        resolver = self.get_resolver(resolver, of_type)
        assert callable(resolver), f'resolver needs to be callable, not {resolver}'

        assert source is None or isinstance(source, str), f'source= has to be of type str'
        self.source = source

        super().__init__(type=of_type._type, resolver=functools.partial(self.resolve, resolver), args={}, **kwargs)

    @classmethod
    def resolve(cls, resolver: Resolver, obj, info: graphql.ResolveInfo, **kwargs):
        return resolver(obj, info, kwargs)

    def __repr__(self) -> str:
        return f'<Field: {repr(self.type)}>'

    def get_internal_name(self, name: str) -> str:
        return self.source or name

    def resolve_field(self, obj, info: graphql.ResolveInfo, args: ResolveArgs):
        if obj is None:
            return None
        name = self.get_internal_name(info.field_name)
        if isinstance(obj, dict):
            value = obj.get(name)
        else:
            value = getattr(obj, name, None)
        return value

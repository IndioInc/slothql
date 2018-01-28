import inspect
import functools
from typing import Union, Type, Callable

import graphql
from graphql.type.definition import GraphQLType

from slothql.utils import LazyInitMixin

from .list import ListMixin
from .resolver import Resolver


class Field(LazyInitMixin, ListMixin, graphql.GraphQLField):
    __slots__ = ()

    @classmethod
    def get_default_resolver(cls, of_type):
        from slothql import types
        if isinstance(of_type, types.Object):
            return lambda obj, info: of_type.resolve(cls.resolve_field(obj, info), info)
        return cls.resolve_field

    def get_resolver(self, resolver, of_type):
        return Resolver(self, resolver).func or self.get_default_resolver(of_type)

    @staticmethod
    def resolve_lazy_type(of_type):
        assert inspect.isclass(of_type) and issubclass(of_type, GraphQLType) or isinstance(of_type, GraphQLType) or inspect.isfunction(of_type), \
            f'"of_type" needs to be a valid GraphQlType or a lazy reference'
        of_type = of_type() if inspect.isfunction(of_type) else of_type
        of_type = of_type() if inspect.isclass(of_type) else of_type
        return of_type

    def __init__(self, of_type: Union[Type[GraphQLType], Callable], resolver=None, **kwargs):
        of_type = self.resolve_lazy_type(of_type)
        resolver = self.get_resolver(resolver, of_type)
        assert callable(resolver), f'resolver needs to be callable, not {resolver}'

        super().__init__(type=of_type, resolver=functools.partial(self.resolve, resolver), **kwargs)

    @classmethod
    def resolve(cls, resolver, obj, info: graphql.ResolveInfo):
        return resolver(obj, info)

    def __repr__(self) -> str:
        return f'<Field: {repr(self.type)}>'

    @classmethod
    def resolve_field(cls, obj, info: graphql.ResolveInfo):
        if obj is None:
            return None
        name = info.field_name
        if isinstance(obj, dict):
            value = obj.get(name)
        else:
            value = getattr(obj, name, None)
        return value

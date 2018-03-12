import functools

from cached_property import cached_property

import graphql

from slothql import types
from slothql.utils import LazyInitMixin
from slothql.arguments.utils import parse_argument
from slothql.types.base import LazyType, resolve_lazy_type, BaseType

from .resolver import get_resolver, Resolver, PartialResolver, ResolveArgs, is_valid_resolver


class Field(LazyInitMixin):
    def get_default_resolver(self, of_type: BaseType) -> Resolver:
        if isinstance(of_type, types.Object):
            return lambda obj, info, args: of_type.resolve(self.resolve_field(obj, info, args), info, args)
        return self.resolve_field

    def get_resolver(self, resolver: PartialResolver, of_type: BaseType) -> Resolver:
        return get_resolver(self, resolver) or self.get_default_resolver(of_type)

    def __init__(self, of_type: LazyType, resolver: PartialResolver = None, source: str = None, **kwargs):
        self._type = of_type

        assert resolver is None or is_valid_resolver(resolver), f'Resolver has to be callable, but got {resolver}'
        self._resolver = resolver

        assert source is None or isinstance(source, str), f'source= has to be of type str'
        self.source = source

        self.many = kwargs.pop('many', False)
        assert isinstance(self.many, bool), f'many has to be of type bool, not {self.many}'

    @cached_property
    def of_type(self) -> BaseType:
        resolved_type = resolve_lazy_type(self._type)
        assert isinstance(resolved_type, BaseType), \
            f'{self} "of_type" needs to be of type BaseType, not {resolved_type}'
        return resolved_type

    @cached_property
    def resolver(self) -> Resolver:
        resolver = self.get_resolver(self._resolver, self.of_type)
        assert callable(resolver), f'resolver needs to be callable, not {resolver}'
        return functools.partial(self.resolve, resolver)

    @cached_property
    def args(self) -> dict:
        return self.of_type.args() if isinstance(self.of_type, types.Object) else {}

    @cached_property
    def filters(self) -> dict:
        return self.of_type.filters() if isinstance(self.of_type, types.Object) else {}

    def apply_filters(self, resolved, args: dict):
        for field_name, value in args.items():
            filter_set = self.filters[field_name]
            resolved = filter_set.apply(resolved, field_name, value)
        return resolved

    def resolve(self, resolver: Resolver, obj, info: graphql.ResolveInfo, **kwargs):
        args = {name: parse_argument(value) for name, value in kwargs.items()}
        resolved = resolver(obj, info, args)
        return self.apply_filters(resolved, args) if self.many else resolved

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

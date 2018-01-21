import inspect
import functools
from typing import Union, Type

import graphql
from graphql.type.definition import GraphQLType

from .list import ListMixin
from .resolver import Resolver


class Field(ListMixin, graphql.GraphQLField):
    @property
    def default_resolver(self):
        return self.resolve_field

    def get_resolver(self, resolver):
        return Resolver(self, resolver).func or self.default_resolver

    def __init__(self, of_type: Union[GraphQLType, Type[GraphQLType]], resolver=None, **kwargs):
        of_type = of_type() if inspect.isclass(of_type) else of_type
        assert isinstance(of_type, GraphQLType), f'"of_type" needs to be a valid GraphQlType'

        resolver = self.get_resolver(resolver)
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
        return value() if callable(value) else value

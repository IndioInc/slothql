import inspect
from functools import partial

import graphql
from graphql.type.definition import GraphQLType


class Field(graphql.GraphQLField):
    def __init__(self, of_type, resolver=None, args=None, deprecation_reason=None, description=None):
        of_type = of_type() if inspect.isclass(of_type) else of_type
        assert isinstance(of_type, GraphQLType), f'"of_type" needs to be a valid GraphQlType'
        assert resolver is None or callable(resolver), f'resolver needs to be callable, not {resolver}'
        super().__init__(
            type=of_type,
            args=args,
            resolver=partial(self.resolve, resolver),
            deprecation_reason=deprecation_reason,
            description=description,
        )

    @classmethod
    def resolve(cls, resolver, parent, info: graphql.ResolveInfo):
        if not resolver:
            return None
        return resolver(cls.resolve_field(parent, info.field_name), info)

    def __repr__(self) -> str:
        return f'<Field: {repr(self.type)}>'

    @classmethod
    def resolve_field(cls, obj, field_name: str):
        if isinstance(obj, dict):
            value = obj.get(field_name)
        else:
            value = getattr(obj, field_name, None)
        return value() if callable(value) else value

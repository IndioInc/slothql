import graphql

from slothql.utils import snake_to_camelcase
from .types.base import LazyType, resolve_lazy_type


class Schema(graphql.GraphQLSchema):
    def __init__(self, query: LazyType, mutation=None, subscription=None, directives=None, types=None,
                 auto_camelcase: bool = False):
        query = resolve_lazy_type(query)._type
        super().__init__(
            query=self.construct_graphql_type(query) if auto_camelcase else query,
            mutation=mutation,
            subscription=subscription,
            directives=directives,
            types=types,
        )

    def construct_graphql_type(self, obj):
        if isinstance(obj, graphql.GraphQLObjectType):
            return graphql.GraphQLObjectType(
                name=obj.name,
                fields={
                    snake_to_camelcase(name): graphql.GraphQLField(
                        type=self.construct_graphql_type(field.type),
                        args=field.args,
                        resolver=field.resolver,
                        deprecation_reason=field.deprecation_reason,
                        description=field.description,
                    )
                    for name, field in obj.fields.items()
                },
                interfaces=obj.interfaces,
                is_type_of=obj.is_type_of,
                description=obj.description,
            )
        return obj

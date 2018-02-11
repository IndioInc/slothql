import graphql

from .base import LazyType, resolve_lazy_type


class Schema(graphql.GraphQLSchema):
    def __init__(self, query: LazyType, mutation=None, subscription=None, directives=None, types=None):
        super().__init__(
            query=resolve_lazy_type(query)._type,
            mutation=mutation,
            subscription=subscription,
            directives=directives,
            types=types,
        )

import graphql


class Schema(graphql.GraphQLSchema):
    def __init__(self, query, mutation=None, subscription=None, directives=None, types=None):
        query = query() if callable(query) else query
        super().__init__(
            query=query,
            mutation=mutation,
            subscription=subscription,
            directives=directives,
            types=types,
        )

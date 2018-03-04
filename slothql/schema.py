import graphql
from typing import Iterable

from graphql.type.introspection import IntrospectionSchema

from .types.base import LazyType, resolve_lazy_type
from .type_map import TypeMap


class Schema(graphql.GraphQLSchema):
    def __init__(self, query: LazyType, mutation=None, subscription=None, directives=None, types=None,
                 auto_camelcase: bool = False):
        self.auto_camelcase = auto_camelcase
        query = resolve_lazy_type(query)._type
        assert isinstance(query, graphql.GraphQLObjectType), f'Schema query must be Object Type but got: {query}.'
        if mutation:
            assert isinstance(mutation, graphql.GraphQLObjectType), \
                f'Schema mutation must be Object Type but got: {mutation}.'

        if subscription:
            assert isinstance(subscription, graphql.GraphQLObjectType), \
                f'Schema subscription must be Object Type but got: {subscription}.'

        if types:
            assert isinstance(types, Iterable), f'Schema types must be iterable if provided but got: {types}.'

        self._query = query
        self._mutation = mutation
        self._subscription = subscription
        directives = directives or graphql.specified_directives

        assert all(isinstance(d, graphql.GraphQLDirective) for d in directives), \
            f'Schema directives must be List[GraphQLDirective] if provided but got: {directives}.'
        self._directives = directives

        initial_types = [
            query,
            mutation,
            subscription,
            IntrospectionSchema
        ]
        if types:
            initial_types += types
        self._type_map = TypeMap(initial_types, auto_camelcase=True)

    def get_query_type(self):
        return self._query

    def get_mutation_type(self):
        return self._mutation

    def get_subscription_type(self):
        return self._subscription

    def get_type_map(self):
        return self._type_map

    def get_type(self, name):
        return self._type_map.get(name)

    def get_directives(self):
        return self._directives

    def get_directive(self, name):
        for directive in self.get_directives():
            if directive.name == name:
                return directive

        return None

    def get_possible_types(self, abstract_type):
        return self._type_map.get_possible_types(abstract_type)

    def is_possible_type(self, abstract_type, possible_type):
        return self._type_map.is_possible_type(abstract_type, possible_type)

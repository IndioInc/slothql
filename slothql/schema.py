import collections
from typing import Dict

import graphql
from graphql.type.introspection import IntrospectionSchema
from graphql.type.typemap import GraphQLTypeMap

from slothql.utils import snake_to_camelcase
from .types.base import LazyType, resolve_lazy_type

FieldMap = Dict[str, graphql.GraphQLField]


class CamelCaseTypeMap(GraphQLTypeMap):
    # FIXME: this is a really bad workaround, needs to be fixed ASAP
    _type_map = {}

    def __init__(self, types):
        self.__class__._type_map = {}
        super().__init__(types)

    @classmethod
    def reducer(cls, type_map: dict, of_type):
        if of_type is None:
            return type_map
        return super().reducer(map=type_map, type=cls.get_graphql_type(of_type))

    @classmethod
    def get_graphql_type(cls, of_type):
        if isinstance(of_type, (graphql.GraphQLNonNull, graphql.GraphQLList)):
            return type(of_type)(type=cls.get_graphql_type(of_type.of_type))
        if of_type.name in cls._type_map:
            return cls._type_map[of_type.name]
        if not of_type.name.startswith('__') and isinstance(of_type, graphql.GraphQLObjectType):
            fields = of_type.fields
            of_type = graphql.GraphQLObjectType(
                name=of_type.name,
                fields={},
                interfaces=of_type.interfaces,
                is_type_of=of_type.is_type_of,
                description=of_type.description,
            )
            cls._type_map[of_type.name] = of_type
            of_type.fields = cls.construct_fields(fields)
            cls._type_map[of_type.name] = of_type
        return of_type

    @classmethod
    def construct_fields(cls, fields: FieldMap) -> FieldMap:
        return {
            snake_to_camelcase(name): graphql.GraphQLField(
                type=cls.get_graphql_type(field.type),
                args={snake_to_camelcase(name): arg for name, arg in field.args.items()},
                resolver=field.resolver,
                deprecation_reason=field.deprecation_reason,
                description=field.description,
            )
            for name, field in fields.items()
        }


class Schema(graphql.GraphQLSchema):
    def __init__(self, query: LazyType, mutation=None, subscription=None, directives=None, types=None,
                 auto_camelcase: bool = False):
        query = resolve_lazy_type(query)._type

        assert isinstance(query, graphql.GraphQLObjectType), f'Schema query must be Object Type but got: {query}.'
        if mutation:
            assert isinstance(mutation, graphql.GraphQLObjectType), \
                f'Schema mutation must be Object Type but got: {mutation}.'

        if subscription:
            assert isinstance(subscription, graphql.GraphQLObjectType), \
                f'Schema subscription must be Object Type but got: {subscription}.'

        if types:
            assert isinstance(types, collections.Iterable), \
                f'Schema types must be iterable if provided but got: {types}.'

        self._query = query
        self._mutation = mutation
        self._subscription = subscription
        if directives is None:
            directives = graphql.specified_directives

        assert all(isinstance(d, graphql.GraphQLDirective) for d in directives), \
            f'Schema directives must be List[GraphQLDirective] if provided but got: {directives}.'
        self._directives = directives

        initial_types = [
            query,
            mutation,
            subscription,
            IntrospectionSchema,
        ] + (types or [])
        self._type_map = CamelCaseTypeMap(initial_types) if auto_camelcase else GraphQLTypeMap(initial_types)

    def get_query_type(self):
        return self._type_map[self._query.name]

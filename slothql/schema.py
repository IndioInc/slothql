import collections
import functools
from typing import Dict

import graphql
from graphql.type.introspection import IntrospectionSchema
from graphql.type.typemap import GraphQLTypeMap

import slothql
from slothql.types import scalars
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


class TypeMap(dict):
    def __init__(self, *types: slothql.BaseType):
        super().__init__(functools.reduce(self.type_reducer, types, {}))

    def type_reducer(self, type_map: dict, of_type: slothql.BaseType):
        if of_type._meta.name in type_map:
            assert type_map[of_type._meta.name] == of_type, \
                f'Schema has to contain unique type names, but got multiple types of name `{of_type._meta.name}`'
            return type_map
        type_map[of_type._meta.name] = of_type
        if isinstance(of_type, slothql.Object):
            for field in of_type._meta.fields.values():
                type_map = self.type_reducer(type_map, field.of_type)
        return type_map


class ProxyTypeMap(dict):
    def __init__(self, type_map: TypeMap, to_camelcase: bool = False):
        self.to_camelcase = to_camelcase
        super().__init__(functools.reduce(self.type_reducer, type_map.values(), {}))

    def type_reducer(self, type_map: dict, of_type: slothql.BaseType) -> dict:
        if of_type._meta.name in type_map:
            return type_map

        if isinstance(of_type, slothql.Object):
            graphql_type = graphql.GraphQLObjectType(
                name=of_type._meta.name,
                fields={},
                interfaces=None,
                is_type_of=None,
                description=None,
            )
            type_map[of_type._meta.name] = graphql_type
            graphql_type.fields = {
                (snake_to_camelcase(name) if self.to_camelcase else name): graphql.GraphQLField(
                    type=self.get_type(type_map, field),
                    args=field.args,
                    resolver=field.resolver,
                    deprecation_reason=field.deprecation_reason,
                    description=field.description,
                ) for name, field in of_type._meta.fields.items()
            }
        if isinstance(of_type, scalars.ScalarType):
            type_map[of_type._meta.name] = of_type._type
        return type_map

    def get_type(self, type_map: dict, field: slothql.Field):
        graphql_type = self.type_reducer(type_map, field.of_type)[field.of_type._meta.name]
        if field.many:
            graphql_type = graphql.GraphQLList(type=graphql_type)
        return graphql_type


class Schema(graphql.GraphQLSchema):
    def __init__(self, query: LazyType, mutation=None, subscription=None, directives=None, types=None,
                 auto_camelcase: bool = False):
        type_map = TypeMap(resolve_lazy_type(query))
        graphql_type_map = ProxyTypeMap(type_map, to_camelcase=auto_camelcase)
        query = query and graphql_type_map[resolve_lazy_type(query)._meta.name]
        mutation = None
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
        self._type_map = GraphQLTypeMap(initial_types)

    def build_query_type(self, root_type: slothql.Object) -> graphql.GraphQLObjectType:
        raise NotImplementedError

    def get_query_type(self):
        return self._type_map[self._query.name]

import inspect
import collections
import functools
import typing as t

import graphql
from graphql.type import GraphQLEnumValue
from graphql.type.definition import GraphQLType
from graphql.type.introspection import IntrospectionSchema
from graphql.type.typemap import GraphQLTypeMap

from slothql import ResolveInfo
from .types import scalars, fields, object, base, enum, union
from .types.fields.filter import Filter
from .utils import snake_to_camelcase

from .types.base import LazyType, resolve_lazy_type

FieldMap = t.Dict[str, graphql.GraphQLField]


class TypeMap(dict):
    def __init__(self, *types: t.Type[base.BaseType]):
        super().__init__(functools.reduce(self.type_reducer, types, {}))

    def type_reducer(self, type_map: dict, of_type: t.Type[base.BaseType]):
        if of_type._meta.name in type_map:
            assert (
                type_map[of_type._meta.name] == of_type
            ), f"Schema has to contain unique type names, but got multiple types of name `{of_type._meta.name}`"
            return type_map
        type_map[of_type._meta.name] = of_type
        if issubclass(of_type, object.Object):
            for field in of_type._meta.fields.values():
                type_map = self.type_reducer(type_map, field.of_type)
        return type_map


class ProxyTypeMap(dict):
    def __init__(self, type_map: TypeMap, auto_camelcase: bool = False):
        super().__init__()
        self.auto_camelcase = auto_camelcase
        self.camelcase_type_map = collections.defaultdict(dict)
        for of_type in type_map.values():
            self.get_graphql_type(of_type)

    def make_camelcase(self, type_name: str, field_name: str) -> str:
        if self.auto_camelcase:
            camelcase = snake_to_camelcase(field_name)
            self.camelcase_type_map[type_name][camelcase] = field_name
            return camelcase
        return field_name

    def field_resolver_wrapper(self, field: fields.Field) -> callable:
        @functools.wraps(field.resolver)
        def wrapper(parent, info, **args):
            if self.auto_camelcase:
                if field.filterable:
                    args = {
                        "filter": {
                            self.camelcase_type_map[
                                field.of_type._meta.filter_class._meta.name
                            ][name]: value
                            for name, value in args.get("filter", {}).items()
                        }
                    }
                info.field_name = self.camelcase_type_map[field.parent._meta.name][
                    info.field_name
                ]
                for ast_field in info.field_asts:
                    ast_field.name.value = self.camelcase_type_map[
                        field.parent._meta.name
                    ][ast_field.name.value]
            return field.resolver(parent, ResolveInfo.from_info(info), **args)

        return wrapper

    def get_scalar_type(self, of_type: t.Type[scalars.ScalarType]):
        if issubclass(of_type, scalars.IDType):
            return graphql.GraphQLID
        elif issubclass(of_type, scalars.StringType):
            return graphql.GraphQLString
        elif issubclass(of_type, scalars.BooleanType):
            return graphql.GraphQLBoolean
        elif issubclass(of_type, scalars.IntegerType):
            return graphql.GraphQLInt
        elif issubclass(of_type, scalars.FloatType):
            return graphql.GraphQLFloat
        raise NotImplementedError(f"{of_type} conversion is not implemented")

    def get_graphql_type(self, of_type: t.Type[base.BaseType]) -> GraphQLType:
        assert inspect.isclass(of_type) and issubclass(
            of_type, base.BaseType
        ), f"Expected `{of_type}` to be a subclass of slothql.BaseType"

        if of_type._meta.name in self:
            return self[of_type._meta.name]
        elif issubclass(of_type, scalars.ScalarType):
            graphql_type = self.get_scalar_type(of_type)
        elif issubclass(of_type, enum.Enum):
            return graphql.GraphQLEnumType(
                name=of_type._meta.name,
                values={
                    self.make_camelcase(of_type._meta.name, name): GraphQLEnumValue(
                        value=value.value, description=value.description
                    )
                    for name, value in of_type._meta.enum_values.items()
                },
                description=of_type._meta.description,
            )
        elif issubclass(of_type, union.Union):
            graphql_type = graphql.GraphQLUnionType(
                name=of_type._meta.name,
                types=[self.get_graphql_type(t) for t in of_type._meta.union_types],
                resolve_type=of_type.resolve_type
                and self.type_resolver(of_type.resolve_type),
            )
        elif issubclass(of_type, object.Object):
            graphql_type = graphql.GraphQLObjectType(
                name=of_type._meta.name,
                fields=lambda: {
                    self.make_camelcase(of_type._meta.name, name): graphql.GraphQLField(
                        type=self.get_type(field),
                        args={
                            self.make_camelcase(
                                of_type._meta.name, arg_name
                            ): self.get_argument(arg_field)
                            for arg_name, arg_field in field.arguments.items()
                        },
                        resolver=self.field_resolver_wrapper(field),
                        deprecation_reason=None,
                        description=field.description,
                    )
                    for name, field in of_type._meta.fields.items()
                },
                interfaces=None,
                is_type_of=of_type.is_type_of,
                description=None,
            )
        elif issubclass(of_type, Filter):
            graphql_type = graphql.GraphQLInputObjectType(
                name=of_type._meta.name,
                fields=lambda: {
                    self.make_camelcase(
                        of_type._meta.name, name
                    ): graphql.GraphQLInputObjectField(self.get_input_type(field))
                    for name, field in of_type._meta.fields.items()
                },
            )
        else:
            raise NotImplementedError(f"Unsupported type {of_type}")
        self[graphql_type.name] = graphql_type
        return graphql_type

    def get_type(self, field: object.Field):
        graphql_type = self.get_graphql_type(field.of_type)
        if field.many:
            graphql_type = graphql.GraphQLList(type=graphql_type)
        return graphql_type

    def get_argument(self, field) -> graphql.GraphQLArgument:
        return graphql.GraphQLArgument(type=self.get_input_type(field))

    def get_input_type(self, of_type):
        if inspect.isclass(of_type) and issubclass(of_type, Filter):
            return self.get_graphql_type(of_type)
        if isinstance(of_type, object.Field):
            field_type = of_type.of_type
            if issubclass(field_type, scalars.ScalarType):
                return self.get_scalar_type(field_type)
            elif issubclass(field_type, Filter):
                return self.get_graphql_type(field_type)
        raise NotImplementedError(f"Type conversion for {of_type} is not implemented.")

    def type_resolver(self, resolve_type: t.Callable) -> t.Callable:
        @functools.wraps(resolve_type)
        def wrapper(*args, **kwargs):
            resolved_type: object.Object = resolve_type(*args, **kwargs)
            return self[resolved_type._meta.name]

        return wrapper


class Schema(graphql.GraphQLSchema):
    def __init__(
        self,
        query: LazyType,
        mutation=None,
        subscription=None,
        directives=None,
        types=None,
        auto_camelcase: bool = False,
    ):
        type_map = TypeMap(resolve_lazy_type(query))
        graphql_type_map = ProxyTypeMap(type_map, auto_camelcase=auto_camelcase)
        query = query and graphql_type_map[resolve_lazy_type(query)._meta.name]
        mutation = None
        assert isinstance(
            query, graphql.GraphQLObjectType
        ), f"Schema query must be Object Type but got: {query}."
        assert mutation is None or isinstance(
            mutation, graphql.GraphQLObjectType
        ), f"Schema mutation must be Object Type but got: {mutation}."

        assert subscription is None or isinstance(
            subscription, graphql.GraphQLObjectType
        ), f"Schema subscription must be Object Type but got: {subscription}."

        assert types is None or isinstance(
            types, collections.Iterable
        ), f"Schema types must be iterable if provided but got: {types}."

        self._query = query
        self._mutation = mutation
        self._subscription = subscription
        if directives is None:
            directives = graphql.specified_directives

        assert all(
            isinstance(d, graphql.GraphQLDirective) for d in directives
        ), f"Schema directives must be List[GraphQLDirective] if provided but got: {directives}."
        self._directives = directives

        initial_types = [query, mutation, subscription, IntrospectionSchema] + (
            types or []
        )
        self._type_map = GraphQLTypeMap(initial_types)

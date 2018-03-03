import operator
import functools
from typing import Iterable, Callable, Dict, Union

import graphql
from graphql.language import ast

Filter = Callable[[Iterable, ast.Value], Iterable]
FilterValue = Union[int, str, bool, list]


def field_getter(obj, field_name):
    return getattr(obj, field_name, obj.get(field_name))


def filter_function(iterable: Iterable, field_name: str, value: FilterValue, comparator: Callable) -> Iterable:
    yield from (i for i in iterable if comparator(field_getter(i, field_name), value))


equals = functools.partial(filter_function, comparator=operator.eq)
not_equals = functools.partial(filter_function, comparator=operator.ne)
is_in = functools.partial(filter_function, comparator=lambda a, b: a in b)


class FilterSet(dict):
    def __init__(self, initial: dict, default_filter: str):
        super().__init__(initial)
        assert default_filter in self
        self.default_filter = default_filter

    def apply(self, collection: Iterable, field_name: str, value: FilterValue) -> Iterable:
        new_collection = collection
        if isinstance(value, dict):
            for filter_func, filter_value in value.items():
                if filter_func not in self:
                    raise NotImplementedError(
                        f'Invalid query function `{filter_func}`. Argument validation not implemented')
                new_collection = self[filter_func](new_collection, field_name, filter_value)
        else:
            new_collection = self[self.default_filter](new_collection, field_name, value)
        return list(new_collection)


IntegerFilterSet = FilterSet({
    'eq': equals,
    'ne': not_equals,
}, 'eq')

StringFilterSet = FilterSet({
    'eq': equals,
    'ne': not_equals,
}, 'eq')

IDFilterSet = FilterSet({
    'eq': equals,
    'in': is_in,
}, 'eq')


def get_filter_fields(of_type: graphql.GraphQLScalarType) -> Dict[str, graphql.GraphQLField]:
    if of_type == graphql.GraphQLID:
        return IDFilterSet
    elif of_type == graphql.GraphQLString:
        return StringFilterSet
    elif of_type == graphql.GraphQLInt:
        return IntegerFilterSet
    return {}

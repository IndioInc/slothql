import operator
import functools
import collections
from typing import Iterable, Callable, Dict, Union, Tuple

import graphql
from graphql.language import ast

Filter = Callable[[Iterable, ast.Value], Iterable]
FilterValue = Union[int, str, bool]
ScalarValueTypes = (ast.BooleanValue, ast.IntValue, ast.FloatValue, ast.StringValue, ast.EnumValue)


def field_getter(obj, field_name):
    return getattr(obj, field_name, obj.get(field_name))


def attribute_getter():
    pass


def filter_function(iterable: Iterable, field_name: str, value: FilterValue, comparator: Callable) -> Iterable:
    for i in iterable:
        print(field_getter(i, field_name), value)
    return [i for i in iterable if comparator(field_getter(i, field_name), value)]


equals = functools.partial(filter_function, comparator=operator.eq)
not_equals = functools.partial(filter_function, comparator=operator.ne)


class FilterSet(collections.OrderedDict):
    def __init__(self, initial: dict, default_filter: str):
        super().__init__(initial)
        assert default_filter in self
        self.default_filter = default_filter

    def apply(self, collection: Iterable, field_name: str, value: ast.Value) -> Iterable:
        new_collection = collection
        if isinstance(value, ast.ObjectValue):
            print(value)
        elif isinstance(value, ScalarValueTypes):
            new_collection = self[self.default_filter](new_collection, field_name, value.value)
        else:
            raise NotImplementedError(f'Unsupported Value type: {repr(value)}')
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
}, 'eq')


def get_filter_fields(of_type: graphql.GraphQLScalarType) -> Dict[str, graphql.GraphQLField]:
    if of_type == graphql.GraphQLID:
        return IDFilterSet
    elif of_type == graphql.GraphQLString:
        return StringFilterSet
    elif of_type == graphql.GraphQLInt:
        return IntegerFilterSet
    return {}

from collections import OrderedDict
from typing import Iterable, Callable, Optional, Dict

import graphql
from graphql.language.ast import Value

Filter = Callable[[Iterable, Value], Iterable]


def equals(iterable: Iterable, value: Value) -> Iterable:
    yield from (i for i in iterable if i == value)


def not_equals(iterable: Iterable, value: Value) -> Iterable:
    yield from (i for i in iterable if i != value)


def greater_than(iterable: Iterable, value: Value) -> Iterable:
    yield from (i for i in iterable if i >= value)


def less_than(iterable: Iterable, value: Value) -> Iterable:
    yield from (i for i in iterable if i <= value)


class FilterSet(OrderedDict):
    def __init__(self, of_type: graphql.GraphQLScalarType, initial: dict, default_filter: str):
        self.of_type = of_type
        super().__init__(initial)
        assert default_filter in self
        self.default_filter = default_filter

    def apply_filter(self, collection: Iterable, filter_function: str) -> Iterable:
        yield from self[filter_function](collection)

    def apply(self, collection: Iterable, filter_functions: Iterable[str]) -> Iterable:
        new_collection = collection
        for filter_function in filter_functions:
            new_collection = self[filter_function](collection)
        return new_collection

    @property
    def fields(self) -> Dict[str, graphql.GraphQLField]:
        return {key: graphql.GraphQLInputObjectField(self.of_type) for key in self}


IntegerFilterSet = FilterSet(graphql.GraphQLInt, {
    'e': equals,
    'ne': not_equals,
    'gt': greater_than,
    'lt': less_than,
}, 'e')

StringFilterSet = FilterSet(graphql.GraphQLString, {
    'e': equals,
    'ne': not_equals,
}, 'e')


def get_filter_fields(of_type: graphql.GraphQLScalarType) -> Dict[str, graphql.GraphQLField]:
    if of_type == graphql.GraphQLString:
        return StringFilterSet.fields
    elif of_type == graphql.GraphQLInt:
        return IntegerFilterSet.fields
    return {}

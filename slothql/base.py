import inspect
from typing import Union, Type, Callable

from graphql.type.definition import GraphQLType


class BaseType:
    def __init__(self, type_: GraphQLType):
        self._type = type_


LazyType = Union[Type[BaseType], BaseType, Callable]


def resolve_lazy_type(lazy_type: LazyType) -> BaseType:
    assert inspect.isclass(lazy_type) and issubclass(lazy_type, BaseType) or isinstance(lazy_type, BaseType) \
           or inspect.isfunction(lazy_type), f'"lazy_type" needs to inherit from BaseType or be a lazy reference'
    of_type = lazy_type() if inspect.isfunction(lazy_type) else lazy_type
    of_type = of_type() if inspect.isclass(of_type) else of_type
    return of_type

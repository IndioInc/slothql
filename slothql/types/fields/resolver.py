import inspect
import functools
from typing import Callable, Dict, Optional, Any, Union

import graphql
from graphql.language.ast import Value

from slothql.utils.functional import is_method, get_function_signature

ResolveArgs = Dict[str, Value]
PartialResolver = Union[
    Callable[[Any, graphql.ResolveInfo, ResolveArgs], Any],
    Callable[[Any, graphql.ResolveInfo], Any],
    Callable[[Any], Any],
    Callable[[], Any],
]
Resolver = Callable[[Any, graphql.ResolveInfo, ResolveArgs], Any]


def _get_function(field, resolver: PartialResolver = None) -> Optional[PartialResolver]:
    if resolver is None:
        return None
    if isinstance(resolver, staticmethod):
        return resolver.__func__
    if isinstance(resolver, classmethod):
        return functools.partial(resolver.__func__, type(field))
    if is_method(resolver):
        return functools.partial(resolver, field)
    return resolver


def _inject_missing_args(func: PartialResolver) -> Resolver:
    signature, arg_count = get_function_signature(func)
    assert arg_count <= 3, f'{func} expected arguments to be of signature (parent, info, args), received {signature}'
    if arg_count < 3:
        @functools.wraps(func)
        def resolver(parent, info, args):
            if arg_count == 0:
                return func()
            elif arg_count == 1:
                return func(parent)
            return func(parent, info)

        return resolver
    return func


def get_resolver(field, resolver: PartialResolver) -> Resolver:
    func = _get_function(field, resolver)
    return func and _inject_missing_args(func)


def is_valid_resolver(resolver: PartialResolver) -> bool:
    return inspect.isfunction(resolver) or isinstance(resolver, (classmethod, staticmethod))

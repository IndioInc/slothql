import functools
import inspect
import typing as t

import graphql
from graphql.language import ast

from slothql.utils.functional import get_function_signature, is_method

ResolveArgs = t.Dict[str, ast.Value]
PartialResolver = t.Union[
    t.Callable[[t.Any, graphql.ResolveInfo, ResolveArgs], t.Any],
    t.Callable[[t.Any, graphql.ResolveInfo], t.Any],
    t.Callable[[t.Any], t.Any],
    t.Callable[[], t.Any],
]
Resolver = t.Callable[[t.Any, graphql.ResolveInfo, ResolveArgs], t.Any]


def _get_function(
    field, resolver: PartialResolver = None
) -> t.Optional[PartialResolver]:
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
    assert (
        arg_count <= 3
    ), f"{func} expected arguments to be of signature (parent, info, args), received {signature}"
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


def get_resolver(field, resolver: PartialResolver) -> t.Optional[Resolver]:
    func = _get_function(field, resolver)
    return func and _inject_missing_args(func)


def is_valid_partial_resolver(resolver: PartialResolver) -> bool:
    return inspect.isfunction(resolver) or isinstance(
        resolver, (classmethod, staticmethod)
    )


def is_valid_resolver(resolver: Resolver) -> bool:
    return callable(resolver)

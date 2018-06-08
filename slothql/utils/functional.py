import inspect
import functools
from typing import Callable, Tuple


def is_method(func):
    return (
        func.__code__.co_varnames and "self" == func.__code__.co_varnames[0]
    )  # FIXME: noqa


def get_function_signature(func: Callable) -> Tuple[inspect.Signature, int]:
    if isinstance(func, functools.partial):
        signature = inspect.signature(func.func)
        return signature, len(signature.parameters) - len(func.args)
    assert callable(func), f"Expected callable, got {func}"
    signature = inspect.signature(func)
    return signature, len(signature.parameters)

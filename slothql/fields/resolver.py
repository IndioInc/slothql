import inspect
import functools


class Resolver:
    @staticmethod
    def is_method(func):
        return func.__code__.co_varnames and 'self' == func.__code__.co_varnames[0]

    def __init__(self, field, resolver):
        func = self.get_function(field, resolver)
        self.func = func and self.inject_missing_args(func)

    @classmethod
    def get_function(cls, field, resolver):
        if resolver is None:
            return None
        if isinstance(resolver, staticmethod):
            return resolver.__func__
        if isinstance(resolver, classmethod):
            return functools.partial(resolver.__func__, type(field))
        if cls.is_method(resolver):
            return functools.partial(resolver, field)
        return resolver

    @classmethod
    def inject_missing_args(cls, func):
        if isinstance(func, functools.partial):
            signature = inspect.signature(func.func)
            arg_count = len(signature.parameters) - len(func.args)
        else:
            assert callable(func), f'Expected callable, got {func}'
            signature = inspect.signature(func)
            arg_count = len(signature.parameters)
        assert arg_count <= 2, \
            f'{func} expected arguments to be of signature (obj, info), received {signature}'
        if arg_count < 2:
            @functools.wraps(func)
            def resolver(obj, info):
                return func() if arg_count == 0 else func(obj)

            return resolver
        return func

import inspect
from typing import Union, Type, Callable, Tuple, Iterable

import graphql

from slothql.utils import is_magic_name, get_attr_fields
from slothql.utils.singleton import Singleton


class BaseOptions:
    __slots__ = 'abstract', 'name', 'description'

    def set_defaults(self):
        for name in (n for n in dir(self) if not is_magic_name(n)):
            if not hasattr(self, name):
                setattr(self, name, None)

    def __init__(self, **kwargs):
        self.set_defaults()
        for name, value in kwargs.items():
            try:
                setattr(self, name, value)
            except AttributeError:
                raise AttributeError(f'Meta received an unexpected attribute "{name} = {value}"')


class BaseMeta(Singleton):
    def __new__(mcs, name: str, bases: Tuple[type], attrs: dict,
                options_class: Type[BaseOptions] = BaseOptions, **kwargs):
        assert 'Meta' not in attrs or inspect.isclass(attrs['Meta']), 'attribute Meta has to be a class'
        cls: BaseMeta = super().__new__(mcs, name, bases, attrs)
        base_option = cls.merge_options(*mcs.get_options_bases(bases))
        meta_attrs = get_attr_fields(attrs['Meta']) if 'Meta' in attrs else {}
        cls._meta = options_class(
            **cls.merge_options(base_option, cls.get_option_attrs(name, base_option, attrs, meta_attrs)),
        )
        return cls

    def get_option_attrs(cls, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict) -> dict:
        defaults = {
            'name': meta_attrs.get('name') or name,
            'abstract': meta_attrs.get('abstract', False),
        }
        return {**meta_attrs, **defaults}

    def merge_options(cls, *options: dict) -> dict:
        result = {}
        for option_set in options:
            for name, value in option_set.items():
                result[name] = cls.merge_field(result.get(name), value)
        return result

    @classmethod
    def get_options_bases(mcs, bases: Tuple[type]) -> Iterable[dict]:
        yield from (
            get_attr_fields(base._meta)
            for base in reversed(bases) if hasattr(base, '_meta') and isinstance(base._meta, BaseOptions)
        )

    @classmethod
    def merge_field(mcs, old, new):
        if isinstance(new, dict):
            return {**(old or {}), **new}
        return new


class BaseType(metaclass=BaseMeta):
    @staticmethod
    def __new__(cls, *more):
        assert not cls._meta.abstract, f'Abstract type {cls.__name__} can not be instantiated'
        return super().__new__(cls)

    @classmethod
    def resolve(cls, parent, info: graphql.ResolveInfo, args: dict):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__


LazyType = Union[Type[BaseType], BaseType, Callable]


def resolve_lazy_type(lazy_type: LazyType) -> BaseType:
    assert (inspect.isclass(lazy_type) and issubclass(lazy_type, BaseType) or isinstance(lazy_type, BaseType)
            or inspect.isfunction(lazy_type)), \
        f'"lazy_type" needs to inherit from BaseType or be a lazy reference, not {lazy_type}'
    of_type = lazy_type() if inspect.isfunction(lazy_type) else lazy_type
    of_type = of_type() if inspect.isclass(of_type) else of_type
    return of_type

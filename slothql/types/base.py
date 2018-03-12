import inspect
from typing import Union, Type, Callable, Tuple, Iterable

from graphql.type.definition import GraphQLType

from slothql.utils import is_magic_name, get_attr_fields
from slothql.utils.singleton import Singleton


class TypeOptions:
    __slots__ = 'abstract', 'name', 'description'

    def set_defaults(self):
        for name in (n for n in dir(self) if not is_magic_name(n)):
            if not hasattr(self, name):
                setattr(self, name, None)

    def __init__(self, attrs: dict):
        self.set_defaults()
        for name, value in attrs.items():
            try:
                setattr(self, name, value)
            except AttributeError:
                raise AttributeError(f'Meta received an unexpected attribute "{name} = {value}"')


class TypeMeta(Singleton):
    def __new__(mcs, name: str, bases: Tuple[type], attrs: dict,
                options_class: Type[TypeOptions] = TypeOptions, **kwargs):
        assert 'Meta' not in attrs or inspect.isclass(attrs['Meta']), 'attribute Meta has to be a class'
        meta_attrs = get_attr_fields(attrs['Meta']) if 'Meta' in attrs else {}
        base_option = mcs.merge_options(*mcs.get_options_bases(bases))
        meta = options_class(mcs.merge_options(base_option, mcs.get_option_attrs(name, base_option, attrs, meta_attrs)))
        cls = super().__new__(mcs, name, bases, attrs)
        cls._meta = meta
        return cls

    @classmethod
    def get_option_attrs(mcs, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict) -> dict:
        defaults = {
            'name': meta_attrs.get('name') or name,
            'abstract': meta_attrs.get('abstract', False),
        }
        return {**meta_attrs, **defaults}

    @classmethod
    def merge_options(mcs, *options: dict):
        result = {}
        for option_set in options:
            for name, value in option_set.items():
                result[name] = mcs.merge_field(result.get(name), value)
        return result

    @classmethod
    def get_options_bases(mcs, bases: Tuple[type]) -> Iterable[dict]:
        yield from (
            get_attr_fields(base._meta)
            for base in reversed(bases) if hasattr(base, '_meta') and isinstance(base._meta, TypeOptions)
        )

    @classmethod
    def merge_field(mcs, old, new):
        if isinstance(new, dict):
            return {**(old or {}), **new}
        return new


class BaseType(metaclass=TypeMeta):
    @staticmethod
    def __new__(cls, *more):
        assert not cls._meta.abstract, f'Abstract type {cls.__name__} can not be instantiated'
        return super().__new__(cls)

    def __init__(self, type_: GraphQLType):
        self._type = type_

    @classmethod
    def get_output_type(cls) -> GraphQLType:
        raise NotImplementedError


LazyType = Union[Type[BaseType], BaseType, Callable]


def resolve_lazy_type(lazy_type: LazyType) -> BaseType:
    assert inspect.isclass(lazy_type) and issubclass(lazy_type, BaseType) or isinstance(lazy_type, BaseType) \
           or inspect.isfunction(lazy_type), f'"lazy_type" needs to inherit from BaseType or be a lazy reference'
    of_type = lazy_type() if inspect.isfunction(lazy_type) else lazy_type
    of_type = of_type() if inspect.isclass(of_type) else of_type
    return of_type

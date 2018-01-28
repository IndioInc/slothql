import inspect
from typing import Tuple, Type, Iterable

import graphql

from slothql.fields import Field
from slothql.utils import is_magic_name, get_attr_fields
from slothql.utils.singleton import Singleton


class ObjectOptions:
    __slots__ = 'object', 'abstract', 'fields'

    def set_defaults(self):
        for name in (n for n in dir(self) if not is_magic_name(n)):
            if not hasattr(self, name):
                setattr(self, name, None)
        self.fields = {}

    def __init__(self, attrs: dict):
        self.set_defaults()
        for name, value in attrs.items():
            try:
                setattr(self, name, value)
            except AttributeError:
                raise AttributeError(f'Meta received an unexpected attribute "{name} = {value}"')


class ObjectMeta(Singleton):
    __slots__ = ()

    def __new__(mcs, name, bases, attrs: dict, options_class: Type[ObjectOptions] = ObjectOptions, **kwargs):
        assert 'Meta' not in attrs or inspect.isclass(attrs['Meta']), 'attribute Meta has to be a class'
        meta_attrs = get_attr_fields(attrs['Meta']) if 'Meta' in attrs else {}
        base_option = mcs.merge_options(*mcs.get_options_bases(bases))
        meta = options_class(mcs.merge_options(base_option, mcs.get_option_attrs(base_option, attrs, meta_attrs)))
        cls = super().__new__(mcs, name, bases, attrs)

        assert meta.abstract or meta.fields, \
            f'"{name}" has to provide some fields, or use "class Meta: abstract = True"'
        cls._meta = meta
        return cls

    @classmethod
    def get_option_attrs(mcs, base_attrs: dict, attrs: dict, meta_attrs: dict) -> dict:
        abstract = meta_attrs.pop('abstract', False)
        return {**meta_attrs, **{
            'fields': {name: field for name, field in attrs.items() if isinstance(field, Field)},
            'abstract': abstract,
        }}

    @classmethod
    def merge_options(mcs, *options: dict):
        result = {}
        for option_set in options:
            for name, value in option_set.items():
                result[name] = mcs.merge_field(result.get(name), value)
        return result

    @classmethod
    def get_options_bases(mcs, bases: Tuple[Type['Object']]) -> Iterable[dict]:
        yield from (
            get_attr_fields(base._meta)
            for base in reversed(bases) if hasattr(base, '_meta') and isinstance(base._meta, ObjectOptions)
        )

    @classmethod
    def merge_field(mcs, old, new):
        if isinstance(new, dict):
            return {**(old or {}), **new}
        return new


class Object(graphql.GraphQLObjectType, metaclass=ObjectMeta):
    @classmethod
    def __new__(cls, *more):
        assert not cls._meta.abstract, f'Abstract type {cls.__name__} can not be instantiated'
        return super().__new__(*more)

    def __init__(self, **kwargs):
        super().__init__(name=self.__class__.__name__, fields=self._meta.fields, **kwargs)

    class Meta:
        abstract = True

    @classmethod
    def resolve(cls, obj, info):
        return obj

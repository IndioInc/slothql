import inspect
from typing import Tuple, Type, Iterable, Dict

import graphql

from slothql.fields import Field
from slothql.utils import is_magic_name, get_attr_fields


class ObjectOptions:
    __slots__ = ('abstract', 'fields')

    def set_defaults(self):
        for name in (n for n in dir(self) if not is_magic_name(n)):
            if not hasattr(self, name):
                setattr(self, name, None)
        self.fields = {}

    def __init__(self, base_attrs: Iterable[dict], meta_attrs: dict, obj_attrs: dict):
        self.set_defaults()
        attrs = self.merge_attributes(
            *base_attrs,
            {**meta_attrs, **{'abstract': meta_attrs.get('abstract', False)}}
        )
        for name, value in attrs.items():
            setattr(self, name, value)
        self.fields = self.get_fields(meta_attrs, obj_attrs)

    @classmethod
    def overwrite_field(cls, name: str, base, field):
        if isinstance(field, dict):
            return {**(base or {}), **field}
        return field

    @classmethod
    def merge_attributes(cls, *obj_dicts: dict):
        result = {}
        for obj_dict in obj_dicts:
            for name, value in obj_dict.items():
                result[name] = cls.overwrite_field(name, result.get(name), value)
        return result

    def get_fields(self, meta_attrs: dict, attrs: dict) -> Dict[str, Field]:
        return {**self.fields, **{
            name: field for name, field in attrs.items() if isinstance(field, Field)
        }}


class ObjectMeta(type):
    __slots__ = ()

    def __new__(mcs, name, bases, attrs: dict, options_class: Type[ObjectOptions] = ObjectOptions, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        assert 'Meta' not in attrs or inspect.isclass(attrs['Meta']), 'attribute Meta has to be a class'
        cls._meta = options_class(
            base_attrs=mcs.get_options_bases(bases),
            meta_attrs=get_attr_fields(attrs['Meta']) if 'Meta' in attrs else {},
            obj_attrs=attrs,
        )
        return cls

    @classmethod
    def get_options_bases(mcs, bases: Tuple[type]) -> Iterable[dict]:
        yield from (
            get_attr_fields(base._meta)
            for base in reversed(bases) if hasattr(base, '_meta') and isinstance(base._meta, ObjectOptions)
        )


class Object(graphql.GraphQLObjectType, metaclass=ObjectMeta):
    @classmethod
    def __new__(cls, *more):
        assert not cls._meta.abstract, f'Abstract type {cls.__name__} can not be created'
        return super().__new__(*more)

    def __init__(self):
        super().__init__(
            name=self.__class__.__name__,
            fields=self._meta.fields,
        )

    class Meta:
        abstract = True

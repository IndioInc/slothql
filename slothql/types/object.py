from typing import Type

import graphql

from slothql.types.base import BaseType, TypeMeta, TypeOptions
from slothql.types.fields import Field


class ObjectOptions(TypeOptions):
    __slots__ = 'abstract', 'fields'

    def set_defaults(self):
        super().set_defaults()
        self.fields = {}


class ObjectMeta(TypeMeta):
    __slots__ = ()

    def __new__(mcs, name, bases, attrs: dict, options_class: Type[ObjectOptions] = ObjectOptions, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs, options_class, **kwargs)
        assert cls._meta.abstract or cls._meta.fields, \
            f'"{name}" has to provide some fields, or use "class Meta: abstract = True"'
        return cls

    @classmethod
    def get_option_attrs(mcs, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict) -> dict:
        return {**super().get_option_attrs(name, base_attrs, attrs, meta_attrs), **{
            'fields': {name: field for name, field in attrs.items() if isinstance(field, Field)},
        }}


class Object(BaseType, metaclass=ObjectMeta):
    def __init__(self, **kwargs):
        super().__init__(graphql.GraphQLObjectType(name=self.__class__.__name__, fields=self._meta.fields, **kwargs))

    class Meta:
        abstract = True

    @classmethod
    def resolve(cls, obj, info):
        return obj

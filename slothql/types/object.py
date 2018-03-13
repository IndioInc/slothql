from typing import Type, Dict

import graphql

from slothql.types import scalars
from slothql.arguments.filters import get_filter_fields, FilterSet

from .base import BaseType, BaseMeta, BaseOptions
from .fields import Field


class ObjectOptions(BaseOptions):
    __slots__ = 'abstract', 'fields'

    def set_defaults(self):
        super().set_defaults()
        self.fields = {}


class ObjectMeta(BaseMeta):
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
    class Meta:
        abstract = True

    @classmethod
    def resolve(cls, parent, info: graphql.ResolveInfo, args: dict):
        return parent

    @classmethod
    def filter_args(cls) -> Dict[str, Field]:
        return {
            name: Field(field.of_type)
            for name, field in cls._meta.fields.items() if isinstance(field.of_type, scalars.ScalarType)
        }

    @classmethod
    def filters(cls) -> Dict[str, FilterSet]:
        return {name: get_filter_fields(field.of_type) for name, field in cls._meta.fields.items()}

from typing import Type, Dict

import graphql

from slothql.arguments.filters import get_filter_fields
from slothql.types.base import BaseType, TypeMeta, TypeOptions
from slothql.types.fields import Field
from slothql.arguments.filters import FilterSet


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
    def __init__(self):
        super().__init__(graphql.GraphQLObjectType(name=self.__class__.__name__, fields=self._meta.fields))

    class Meta:
        abstract = True

    @classmethod
    def get_output_type(cls) -> graphql.GraphQLObjectType:
        return graphql.GraphQLObjectType(name=cls.__name__, fields=cls._meta.fields)

    @classmethod
    def resolve(cls, parent, info: graphql.ResolveInfo, args: dict):
        return parent

    @classmethod
    def args(cls) -> Dict[str, graphql.GraphQLArgument]:
        return {name: graphql.GraphQLArgument(graphql.GraphQLString) for name, of_type in cls._meta.fields.items()}

    @classmethod
    def filters(cls) -> Dict[str, FilterSet]:
        return {name: get_filter_fields(field.type) for name, field in cls._meta.fields.items()}

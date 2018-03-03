import graphql
from typing import Type

from graphql.type import GraphQLEnumValue

from .base import BaseType, BaseMeta, BaseOptions


class EnumOptions(BaseOptions):
    __slots__ = 'values',

    def __init__(self, attrs: dict):
        super().__init__(attrs)
        assert self.abstract or self.values, f'"{self.name}" is missing valid `Enum` values'


class EnumMeta(BaseMeta):
    def __new__(mcs, *args, options_class: Type[EnumOptions] = EnumOptions, **kwargs):
        return super().__new__(mcs, *args, options_class, **kwargs)

    @classmethod
    def get_option_attrs(mcs, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict):
        return {**super().get_option_attrs(name, base_attrs, attrs, meta_attrs), **{
            'values': {field_name: field for field_name, field in attrs.items() if isinstance(field, EnumValue)},
        }}


class EnumValue(GraphQLEnumValue):
    pass


class Enum(BaseType, metaclass=EnumMeta):
    class Meta:
        abstract = True

    def __init__(self):
        super().__init__(type_=graphql.GraphQLEnumType(
            name=self._meta.name,
            values=self._meta.values,
        ))

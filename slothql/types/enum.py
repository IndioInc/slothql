from typing import Type

from .base import BaseType, TypeMeta, TypeOptions


class EnumOptions(TypeOptions):
    __slots__ = 'enum_values',

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert self.abstract or self.enum_values, f'"{self.name}" is missing valid `Enum` values'


class EnumMeta(TypeMeta):
    def __new__(mcs, *args, options_class: Type[EnumOptions] = EnumOptions, **kwargs):
        return super().__new__(mcs, *args, options_class, **kwargs)

    @classmethod
    def get_option_attrs(mcs, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict):
        return {**super().get_option_attrs(name, base_attrs, attrs, meta_attrs), **{
            'enum_values': {field_name: field for field_name, field in attrs.items() if isinstance(field, EnumValue)},
        }}


class EnumValue:
    __slots__ = 'value', 'description'

    def __init__(self, value, description: str = None):
        self.value = value
        self.description = description


class Enum(BaseType, metaclass=EnumMeta):
    class Meta:
        abstract = True

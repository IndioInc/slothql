import typing as t

from .base import BaseType, BaseMeta, BaseOptions


class EnumOptions(BaseOptions):
    __slots__ = ("enum_values",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert (
            self.abstract or self.enum_values
        ), f'"{self.name}" is missing valid `Enum` values'


class EnumMeta(BaseMeta):
    def __new__(mcs, *args, options_class: t.Type[EnumOptions] = EnumOptions, **kwargs):
        return super().__new__(mcs, *args, options_class, **kwargs)

    def get_option_attrs(
        cls, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict
    ):
        return {
            **super().get_option_attrs(name, base_attrs, attrs, meta_attrs),
            **{
                "enum_values": {
                    field_name: field
                    for field_name, field in attrs.items()
                    if isinstance(field, EnumValue)
                }
            },
        }


class EnumValue:
    __slots__ = "value", "description"

    def __init__(self, value, description: str = None):
        self.value = value
        self.description = description


class Enum(BaseType, metaclass=EnumMeta):
    _meta: EnumOptions

    class Meta:
        abstract = True

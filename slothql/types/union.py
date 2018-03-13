from typing import Type

from .base import BaseType, BaseOptions, BaseMeta
from .object import Object


class UnionOptions(BaseOptions):
    __slots__ = 'types',

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert self.types or self.abstract, \
            f'"{self.name}".`types` has to be an iterable of Object, not {repr(self.types)}'


class EnumMeta(BaseMeta):
    def __new__(mcs, *args, options_class: Type[UnionOptions] = UnionOptions, **kwargs):
        return super().__new__(mcs, *args, options_class, **kwargs)

    @classmethod
    def get_option_attrs(mcs, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict):
        types = meta_attrs.get('types')
        assert types is None or all(issubclass(t, Object) for t in types), \
            f'`types` have to be an iterable of Object, not {types}'
        return {**super().get_option_attrs(name, base_attrs, attrs, meta_attrs), **{
            'types': tuple(i()._type for i in (types or ())),
        }}


class Union(BaseType, metaclass=EnumMeta):
    class Meta:
        abstract = True

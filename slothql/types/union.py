from typing import Type, Tuple

import slothql

from .base import BaseType, BaseOptions, BaseMeta
from .object import Object


class UnionOptions(BaseOptions):
    __slots__ = ('union_types',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert self.abstract or self.union_types, \
            f'`{self.name}`.`union_types` has to be an iterable of Object, not {repr(self.union_types)}'


class UnionMeta(BaseMeta):
    def __new__(mcs,  name: str, bases: Tuple[type], attrs: dict,
                options_class: Type[UnionOptions] = UnionOptions, **kwargs):
        cls: Type[Union] = super().__new__(mcs, name, bases, attrs, options_class, **kwargs)
        if cls._meta.name is 'Union' and cls._meta.abstract:
            cls.resolve_type = None
        assert (cls._meta.abstract
                or cls.resolve_type
                or all(t.is_type_of for t in cls._meta.union_types)), \
            f'`{cls.__name__}` has to provide a `resolve_type` method' \
            f' or each subtype has to provide a `is_type_of` method'
        return cls

    @classmethod
    def get_option_attrs(mcs, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict):
        union_types = meta_attrs.get('union_types')
        assert union_types is None or all(issubclass(t, Object) for t in union_types), \
            f'`union_types` have to be an iterable of Object, not {union_types}'
        return {**super().get_option_attrs(name, base_attrs, attrs, meta_attrs), **{
            'union_types': union_types or (),
        }}


class Union(BaseType, metaclass=UnionMeta):
    class Meta:
        abstract = True

    @classmethod
    def resolve_type(cls, obj, info: slothql.ResolveInfo):
        """
        This acts only as a template.
        It will be overwritten to None by the metaclass, if not implemented
        """
        pass

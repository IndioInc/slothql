import typing as t

from .. import base
from ..mixins import FieldMetaMixin
from .field import Field


class FilterOptions(base.BaseOptions):
    __slots__ = ('fields',)
    fields: t.Dict[str, Field]

    def set_defaults(self):
        super().set_defaults()
        self.fields = {}


class FilterMeta(FieldMetaMixin, base.BaseMeta):
    _meta: FilterOptions

    def __new__(mcs, name: str, bases: t.Tuple[type], attrs: dict,
                options_class: t.Type[FilterOptions] = FilterOptions, **kwargs):
        return super().__new__(mcs, name, bases, attrs, options_class, **kwargs)

    @classmethod
    def create_class(mcs, name: str, fields: t.Dict[str, Field], description: str = None) -> 'class':
        return FilterMeta(name, (Filter,), {**fields, 'Meta': type('Meta', (), {'description': description})})


class Filter(base.BaseType, metaclass=FilterMeta):
    _meta: FilterOptions

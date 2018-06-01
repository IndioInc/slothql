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

    def create_class(cls, name: str, fields: t.Dict[str, Field], **kwargs) -> 'class':
        return cls.__class__(name, (cls,), {**fields, 'Meta': type('Meta', (), kwargs)})


class Filter(base.BaseType, metaclass=FilterMeta):
    _meta: FilterOptions

    SKIP = object()

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            if name not in self._meta.fields:
                raise TypeError(f"{self}.__init__() got an unexpected keyword argument '{name}'")
        for field_name in self._meta.fields:
            setattr(self, field_name, kwargs.get(field_name, self.SKIP))

    @staticmethod
    def get_field(obj, field_name):
        return obj.get(field_name) if isinstance(obj, dict) else getattr(obj, field_name)

    def apply(self, iterable: t.Iterable) -> t.Iterable:
        for name, value in self.filter_fields.items():
            # FIXME: make generator
            iterable = [i for i in iterable if self.get_field(i, name) == value]
        return iterable

    @property
    def filter_fields(self) -> t.Dict:
        return {
            field_name: getattr(self, field_name)
            for field_name in self._meta.fields
            if getattr(self, field_name) != self.SKIP
        }

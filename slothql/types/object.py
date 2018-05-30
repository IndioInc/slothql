import typing as t

import slothql
from slothql.types.scalars import ScalarType

from .base import BaseType, BaseMeta, BaseOptions
from .mixins import FieldMetaMixin, Resolvable
from .fields import Field
from .fields.filter import Filter


class ObjectOptions(BaseOptions):
    __slots__ = 'fields', 'filter_class'
    fields: t.Dict[str, Field]
    filter_class: t.Type[Filter]

    def set_defaults(self):
        super().set_defaults()
        self.fields = {}


class ObjectMeta(FieldMetaMixin, BaseMeta):
    _meta: ObjectOptions
    __slots__ = ()

    def __new__(mcs, name, bases, attrs: dict, options_class: t.Type[ObjectOptions] = ObjectOptions, **kwargs):
        cls: t.Type[Object] = super().__new__(mcs, name, bases, attrs, options_class, **kwargs)
        if not hasattr(cls, 'is_type_of') or cls._meta.abstract and cls._meta.name is 'Object':
            cls.is_type_of = None
        assert cls._meta.abstract or cls._meta.fields, \
            f'"{name}" has to provide some fields, or use "class Meta: abstract = True"'
        return cls

    def filter_class(cls) -> t.Type[Filter]:
        if not cls._meta.filter_class:
            cls._meta.filter_class = Filter.create_class(cls._meta.name + 'Filter', fields={
                name: field for name, field in cls._meta.fields.items()
                if issubclass(field.of_type, ScalarType)
            })
        return cls._meta.filter_class


class Object(Resolvable, BaseType, metaclass=ObjectMeta):
    _meta: ObjectOptions

    class Meta:
        abstract = True

    @classmethod
    def resolve(cls, resolved: t.Iterable, info: slothql.ResolveInfo, args: dict) -> t.Iterable:
        return cls._meta.filter_class(**args.get('filter', {})).apply(resolved)

    @classmethod
    def is_type_of(cls, obj, info: slothql.ResolveInfo) -> bool:
        """
        This acts only as a template.
        It will be overwritten to None by the metaclass, if not implemented
        """
        pass

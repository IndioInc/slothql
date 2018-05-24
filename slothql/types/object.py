import typing as t

import slothql

from .base import BaseType, BaseMeta, BaseOptions

from .mixins import FieldMetaMixin


class ObjectOptions(BaseOptions):
    __slots__ = 'abstract', 'fields'

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


class Object(BaseType, metaclass=ObjectMeta):
    class Meta:
        abstract = True

    @classmethod
    def resolve(cls, parent, info: slothql.ResolveInfo, args: dict):
        return parent

    @classmethod
    def is_type_of(cls, obj, info: slothql.ResolveInfo) -> bool:
        """
        This acts only as a template.
        It will be overwritten to None by the metaclass, if not implemented
        """
        pass

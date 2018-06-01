import typing as t

import slothql
from slothql.types.fields.resolver import ResolveArgs
from .fields import Field


class FieldMetaMixin(type):
    __slots__ = ()

    def __new__(mcs, name: str, bases: tuple, attrs: dict, options_class, **kwargs):
        assert hasattr(options_class, 'fields'), f'FieldMetaMixin expects `options_class` to have a `fields` attribute'
        cls = super().__new__(mcs, name, bases, attrs, options_class, **kwargs)
        for name, field in cls._meta.fields.items():
            setattr(cls, name, field)
        return cls

    def get_option_attrs(cls, class_name: str, base_attrs: dict, attrs: dict, meta_attrs: dict) -> dict:
        return {
            **super().get_option_attrs(class_name, base_attrs, attrs, meta_attrs),
            **{'fields': {name: field for name, field in attrs.items() if isinstance(field, Field)}},
        }

    def merge_options(cls, *options: dict) -> dict:
        result = super().merge_options(*options)
        result['fields'] = {
            name: Field.reinstantiate(field, name=name, parent=cls)
            for name, field in result.get('fields', {}).items()
        }
        return result


class Resolvable:
    def resolve(self, resolved: t.Iterable, info: slothql.ResolveInfo, args: ResolveArgs, many: bool) -> t.Iterable:
        raise NotImplementedError

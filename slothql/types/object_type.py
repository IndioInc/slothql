import collections
import inspect
from typing import Tuple, Type, Iterable

import graphql

from slothql.fields import Field
from slothql.utils import is_magic_name, get_object_attributes


class ObjectOptions:
    __slots__ = (
        'abstract',
        'fields',
    )

    def __init__(self, bases: Iterable, **kwargs):
        self.abstract = kwargs.get('abstract', False)
        attributes = self.merge_attributes(*reversed([get_object_attributes(base) for base in bases]), kwargs)
        self.fields = attributes.get('fields', {})

    @classmethod
    def merge_attributes(cls, *attr_dicts: dict):
        result = {}
        for obj in attr_dicts:
            for name, value in obj.items():
                if isinstance(value, dict):
                    result[name] = {**result.get(name, {}), **value}
                else:
                    result[name] = value
        return result


class ObjectMeta(type):
    __slots__ = ()

    def __new__(mcs, name, bases, attrs: dict, options_class: Type[ObjectOptions] = ObjectOptions, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        assert 'Meta' not in attrs or inspect.isclass(attrs['Meta']), 'attribute Meta has to be a class'
        cls._meta = options_class(bases=mcs._get_options_bases(bases), **mcs._get_options_kwargs(attrs))
        return cls

    @classmethod
    def _get_options_bases(mcs, bases: Tuple[type]) -> Iterable[ObjectOptions]:
        yield from (base._meta for base in bases if hasattr(base, '_meta') and isinstance(base._meta, ObjectOptions))

    @classmethod
    def _get_options_kwargs(mcs, attrs: dict) -> dict:
        meta = attrs.get('Meta')
        kwargs = {} if not meta else {k: v for k, v in vars(meta).items() if not is_magic_name(k)} if meta else {}
        kwargs.update(abstract=kwargs.get('abstract', False))
        kwargs.update(fields={field: value for field, value in attrs.items() if isinstance(value, Field)})
        return kwargs


class Object(graphql.GraphQLObjectType, metaclass=ObjectMeta):
    @classmethod
    def __new__(cls, *more):
        assert not cls._meta.abstract, f'Abstract type {cls.__name__} can not be created'
        return super().__new__(*more)

    def __init__(self):
        super().__init__(
            name=self.__class__.__name__,
            fields=self._meta.fields,
        )

    class Meta:
        abstract = True

import inspect

import graphql

from slothql.fields import Field
from slothql.utils import is_magic_name


class ObjectTypeOptions:
    __slots__ = (
        'abstract',
        'fields',
    )

    def __init__(self, **kwargs):
        self.abstract = kwargs.get('abstract', False)
        self.fields = kwargs.get('fields', {})


class ObjectTypeMeta(type):
    meta_options_class = ObjectTypeOptions

    def __new__(mcs, name, bases, attrs: dict, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        assert 'Meta' not in attrs or inspect.isclass(attrs['Meta']), 'attribute Meta has to be a class'
        cls._meta = mcs.meta_options_class(**mcs.get_options_kwargs(attrs))
        return cls

    @classmethod
    def get_options_kwargs(mcs, attrs: dict) -> dict:
        meta = attrs.get('Meta')
        kwargs = {k: v for k, v in vars(meta).items() if not is_magic_name(k)} if meta else {}
        kwargs.update(abstract=kwargs.get('abstract', False))
        kwargs.update(fields={field: value for field, value in attrs.items() if isinstance(value, Field)})
        return kwargs


class ObjectType(graphql.GraphQLObjectType, metaclass=ObjectTypeMeta):
    @classmethod
    def __new__(cls, *more):
        assert not cls._meta.abstract, f'Abstract type {cls.__name__} can not be created'
        return super().__new__(*more)

    def __init__(self):
        super().__init__(
            name=self.__class__.__name__,
            fields=(),
        )

    class Meta:
        abstract = True

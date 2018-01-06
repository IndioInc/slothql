import inspect

import graphql

from slothql.utils import is_magic_name


class ObjectTypeOptions:
    __slots__ = (
        'abstract',
        'fields',
    )

    def __init__(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)


class ObjectTypeMeta(type):
    meta_options_class = ObjectTypeOptions

    def __new__(mcs, name, bases, attrs: dict, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        if 'Meta' not in attrs:
            cls._meta = ObjectTypeOptions(abstract=False)
        else:
            assert inspect.isclass(attrs['Meta']), 'attribute Meta has to be a class'
            options_cls = mcs.meta_options_class
            cls._meta = options_cls(**{k: v for k, v in vars(attrs['Meta']).items() if not is_magic_name(k)})
        return cls


class ObjectType(graphql.GraphQLObjectType, metaclass=ObjectTypeMeta):
    @classmethod
    def __new__(cls, *args):
        assert not cls._meta.abstract, f'Abstract type {cls.__name__} can not be initialized'
        return super().__new__(cls, *args)

    def __init__(self):
        super().__init__(
            name=self.__class__.__name__,
            fields=(),
        )

    class Meta:
        abstract = True

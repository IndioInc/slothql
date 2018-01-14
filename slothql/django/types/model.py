from typing import Type, Iterable

from slothql.types.object import Object, ObjectMeta, ObjectOptions


class ModelOptions(ObjectOptions):
    __slots__ = ('model',)

    def __init__(self, base_options: Iterable['ObjectOptions'], **kwargs):
        super().__init__(base_options, **kwargs)
        if not hasattr(self, 'model'):
            self.model = None
        assert self.abstract or self.model, f'"model" is required for object ModelOptions'


class ModelMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs: dict, options_class: Type[ModelOptions] = ModelOptions, **kwargs):
        assert 'Meta' in attrs, f'class {name} is missing Meta class'
        return super().__new__(mcs, name, bases, attrs, options_class, **kwargs)


class Model(Object, metaclass=ModelMeta):
    class Meta:
        abstract = True

import inspect
from typing import Type, Iterable, Dict, Union

from django.db import models

from slothql import Field
from slothql.types.object import Object, ObjectMeta, ObjectOptions
from slothql.django.utils.model import get_model_attrs

from .registry import TypeRegistry


class ModelOptions(ObjectOptions):
    __slots__ = ('model',)

    def __init__(self, base_attrs: Iterable[dict], meta_attrs: dict, obj_attrs: dict):
        super().__init__(base_attrs, meta_attrs, obj_attrs)
        assert self.abstract or self.model, f'"model" is required for object ModelOptions'

    @classmethod
    def overwrite_field(cls, name: str, base, field):
        if name == 'fields' and (isinstance(field, tuple) or field == '__all__'):
            return base
        return super().overwrite_field(name, base, field)

    def get_fields(self, meta_attrs: dict, attrs: dict) -> Dict[str, Field]:
        fields = meta_attrs.get('fields')
        if fields:
            attrs.update(self.resolve_model_fields(fields))
        return super().get_fields(meta_attrs, attrs)

    @classmethod
    def resolve_attr_list(cls, model: Type[models.Model], fields: Iterable[str]) -> dict:
        attrs = {}
        for name, attr in get_model_attrs(model).items():
            if name not in fields:
                continue
            assert not isinstance(attr, TypeRegistry.RELATION_TYPES), \
                f'Related field {name} = {repr(attr)} has to be declared explicitly, to avoid type collision'
            attrs[name] = attr
        return attrs

    @classmethod
    def resolve_all_fields(cls, model: Type[models.Model]) -> dict:
        return {
            name: attr for name, attr in get_model_attrs(model).items()
            if not isinstance(attr, TypeRegistry.RELATION_TYPES)
        }

    @classmethod
    def get_attrs(cls, model: Type[models.Model], fields: Union[str, Iterable[str]]) -> dict:
        if fields == '__all__':
            return cls.resolve_all_fields(model)
        return cls.resolve_attr_list(model, fields)

    def resolve_model_fields(self, fields: Union[str, Iterable[str]]) -> Dict[str, Field]:
        assert fields == '__all__' or isinstance(fields, Iterable) and all(isinstance(f, str) for f in fields), \
            f'Meta.fields need to be an iterable of field names or "__all__", not {fields}'
        assert self.model, f'Meta.model is required when using Meta.fields'
        assert inspect.isclass(self.model) and issubclass(self.model, models.Model), \
            f'Meta.model has to be Model class, received {self.model}'
        model_attrs = self.get_attrs(self.model, fields)
        for name, field in model_attrs.items():
            assert isinstance(field, models.Field), f'"{name}": field cannot be {field}'
        return {name: TypeRegistry().get(field) for name, field in model_attrs.items()}


class ModelMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs: dict, options_class: Type[ModelOptions] = ModelOptions, **kwargs):
        assert 'Meta' in attrs, f'class {name} is missing "Meta" class'
        return super().__new__(mcs, name, bases, attrs, options_class, **kwargs)


class Model(Object, metaclass=ModelMeta):
    class Meta:
        abstract = True

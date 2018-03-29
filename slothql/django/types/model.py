import inspect
from typing import Type, Iterable, Dict, Union

import graphql
from django.db import models

from slothql import Field
from slothql.types.object import Object, ObjectMeta, ObjectOptions
from slothql.django.utils.model import get_model_attrs

from .registry import TypeRegistry


class ModelOptions(ObjectOptions):
    __slots__ = ('model',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert self.abstract or self.model, f'"model" is required for object ModelOptions'


class ModelMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs: dict, options_class: Type[ModelOptions] = ModelOptions, **kwargs):
        assert 'Meta' in attrs, f'class {name} is missing "Meta" class'
        return super().__new__(mcs, name, bases, attrs, options_class, **kwargs)

    @classmethod
    def get_option_attrs(mcs, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict):
        fields = meta_attrs.pop('fields', None)
        if fields:
            model = base_attrs.get('model') or meta_attrs.get('model')
            resolved_fields = mcs.get_meta_fields(model, fields)
            attrs.update({name: resolved_fields[name] for name in set(resolved_fields) - set(attrs)})
        return super().get_option_attrs(name, base_attrs, attrs, meta_attrs)

    @classmethod
    def get_meta_fields(mcs, model: Type[models.Model], fields: Union[str, Iterable[str]]) -> Dict[str, Field]:
        assert fields == '__all__' or isinstance(fields, Iterable) and all(isinstance(f, str) for f in fields), \
            f'Meta.fields needs to be an iterable of field names or "__all__", but received {fields}'
        assert model, f'Meta.model is required when using Meta.fields'
        assert inspect.isclass(model) and issubclass(model, models.Model), \
            f'Meta.model has to be Model class, received {model}'
        model_attrs = mcs.get_attrs(model, fields)
        for name, field in model_attrs.items():
            assert isinstance(field, models.Field), f'"{name}": field cannot be {field}'
        return {name: TypeRegistry().get(field) for name, field in model_attrs.items()}

    @classmethod
    def resolve_attr_list(mcs, model: Type[models.Model], fields: Iterable[str]) -> dict:
        attrs = {}
        model_attrs = get_model_attrs(model)
        for name in fields:
            assert name in model_attrs, f'"{name}" is not a valid field for model "{model.__name__}"'
        for name, attr in model_attrs.items():
            if name not in fields:
                continue
            assert not isinstance(attr, TypeRegistry.RELATION_TYPES), \
                f'"{name}" has to be declared explicitly, to avoid type collisions'
            attrs[name] = attr
        return attrs

    @classmethod
    def resolve_all_fields(mcs, model: Type[models.Model]) -> dict:
        return {
            name: attr for name, attr in get_model_attrs(model).items()
            if not isinstance(attr, TypeRegistry.RELATION_TYPES)
        }

    @classmethod
    def get_attrs(mcs, model: Type[models.Model], fields: Union[str, Iterable[str]]) -> dict:
        if fields == '__all__':
            return mcs.resolve_all_fields(model)
        return mcs.resolve_attr_list(model, fields)


class Model(Object, metaclass=ModelMeta):
    class Meta:
        abstract = True

    @classmethod
    def filter_queryset(cls, queryset: models.QuerySet, args: dict):
        assert isinstance(queryset, models.QuerySet), f'expected QuerySet, received {repr(queryset)}'
        return queryset.filter()

    @classmethod
    def resolve(cls, parent, info: graphql.ResolveInfo, args: dict):
        if parent is None:
            queryset = cls._meta.model._default_manager.get_queryset()
        else:
            queryset = parent.get_queryset() if isinstance(parent, models.Manager) else parent
        return cls.filter_queryset(queryset, args)

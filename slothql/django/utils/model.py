from typing import Type, Dict, Iterable, Tuple

from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel


def get_model_attrs(model: Type[models.Model]) -> dict:
    return {
        field.name: field for field in model._meta.get_fields()
    }


def get_selectable_relations(model: Type[models.Model]) -> Dict[str, Type[models.Model]]:
    return {field.name: field.related_model for field in model._meta.get_fields()
            if isinstance(field, models.ForeignKey)}


def get_related_fields(model: Type[models.Model]) -> Iterable[Tuple[str, models.Model]]:
    for name, descriptor in vars(model).items():
        if isinstance(getattr(descriptor, 'rel', None), ForeignObjectRel):
            yield name, descriptor.rel.related_model if getattr(descriptor, 'reverse', True) else descriptor.rel.model
        elif isinstance(getattr(descriptor, 'field', None), models.Field):
            yield name, descriptor.field.related_model
        elif isinstance(getattr(descriptor, 'related', None), ForeignObjectRel):
            yield name, descriptor.related.related_model


def get_relations(model: Type[models.Model]) -> Dict[str, models.Model]:
    return dict(get_related_fields(model))

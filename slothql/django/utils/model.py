import typing as t

from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel


class Relation(t.NamedTuple):
    name: str
    model: t.Type[models.Model]

    @classmethod
    def get_selectable(cls, model: t.Type[models.Model]) -> t.Iterable['Relation']:
        yield from (
            Relation(name=field.name, model=field.related_model)
            for field in model._meta.get_fields() if field_is_selectable(field)
        )


def field_is_selectable(field: models.Field) -> bool:
    return isinstance(field, models.ForeignKey)


def field_is_prefetchable(field: models.Field) -> bool:
    raise NotImplementedError


def get_model_attrs(model: t.Type[models.Model]) -> dict:
    return {
        field.name: field for field in model._meta.get_fields()
    }


def get_selectable_relations(model: t.Type[models.Model]) -> t.Dict[str, t.Type[models.Model]]:
    return {field.name: field.related_model for field in model._meta.get_fields()
            if isinstance(field, models.ForeignKey)}


def get_related_fields(model: t.Type[models.Model]) -> t.Iterable[t.Tuple[str, models.Model]]:
    for name, descriptor in vars(model).items():
        if isinstance(getattr(descriptor, 'rel', None), ForeignObjectRel):
            yield name, descriptor.rel.related_model if getattr(descriptor, 'reverse', True) else descriptor.rel.model
        elif isinstance(getattr(descriptor, 'field', None), models.Field):
            yield name, descriptor.field.related_model
        elif isinstance(getattr(descriptor, 'related', None), ForeignObjectRel):
            yield name, descriptor.related.related_model


def get_relations(model: t.Type[models.Model]) -> t.Dict[str, models.Model]:
    return dict(get_related_fields(model))

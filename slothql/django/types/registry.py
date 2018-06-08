import inspect
import typing as t

from django.db import models

import slothql
from slothql.utils.singleton import Singleton


class TypeRegistry(metaclass=Singleton):
    RELATION_TYPES = (
        models.ManyToManyField,
        models.ForeignKey,
        models.ManyToOneRel,
        models.OneToOneField,
        models.OneToOneRel,
    )
    _type_mapping: t.Dict[t.Type[models.Field], t.Type[slothql.Field]] = {}

    def register(
        self, django_field: t.Type[models.Field], field_resolver: t.Type[slothql.Field]
    ):
        assert inspect.isclass(django_field) and issubclass(
            django_field, models.Field
        ), f"Expected django_field to be a subclass of django.db.models.Field, but got: {repr(django_field)}"
        assert inspect.isclass(field_resolver) and issubclass(
            field_resolver, slothql.Field
        ), f"Expected field_resolver to be a subclass of slothql.Field, but got {repr(field_resolver)}"
        self._type_mapping[django_field] = field_resolver

    def unregister(self, django_field: t.Type[models.Field]):
        del self._type_mapping[django_field]

    def clear(self):
        self._type_mapping.clear()

    def get(self, django_field: models.Field) -> slothql.Field:
        if type(django_field) not in self._type_mapping:
            raise NotImplementedError(
                f"{repr(django_field)} field conversion is not implemented"
            )
        return self._type_mapping[type(django_field)]()

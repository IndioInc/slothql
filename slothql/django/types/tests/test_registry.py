import pytest
from unittest import mock

from django.db import models

import slothql

from ..registry import TypeRegistry


def test_singleton():
    assert id(TypeRegistry()) == id(TypeRegistry())


def test_register_field(type_registry: TypeRegistry):
    type_registry.register(models.Field, slothql.Boolean)
    assert slothql.Boolean is type_registry._type_mapping[models.Field]


@pytest.mark.parametrize("field", (models.Model, models.Field()))
def test_register_field__invalid_django_field(field, type_registry: TypeRegistry):
    with pytest.raises(AssertionError) as exc_info:
        type_registry.register(field, mock.Mock(spec=slothql.Field))
    assert str(exc_info.value).startswith("Expected django_field to be a subclass")


def test_clear(type_registry: TypeRegistry):
    type_registry._type_mapping = {"field": "whatever"}  # type: ignore
    type_registry.clear()
    assert type_registry._type_mapping == {}


def test_unregister(type_registry: TypeRegistry):
    type_registry._type_mapping = {  # type: ignore
        models.CharField: "whatever",
        models.TextField: "wtf",
    }
    type_registry.unregister(models.CharField)
    assert type_registry._type_mapping == {models.TextField: "wtf"}


def test_get(type_registry: TypeRegistry):
    type_registry._type_mapping = {models.CharField: slothql.Boolean}
    assert isinstance(type_registry.get(models.CharField()), slothql.Boolean)


def test_get__not_supported(type_registry: TypeRegistry):
    type_registry._type_mapping = {bool: True, str: "wtf"}  # type: ignore
    with pytest.raises(NotImplementedError):
        type_registry.get(42)

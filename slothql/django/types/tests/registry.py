import pytest
from unittest import mock

from django.db import models

import slothql

from ..registry import TypeRegistry


def test_singleton():
    assert id(TypeRegistry()) == id(TypeRegistry())


def test_register_field(type_registry: TypeRegistry):
    field = mock.Mock(spec=slothql.Field)
    type_registry.register(models.Field, field)
    assert type_registry._type_mapping[models.Field] == field


def test_register_field__invalid_django_field(type_registry: TypeRegistry):
    with pytest.raises(AssertionError):
        type_registry.register(models.Model, mock.Mock(spec=slothql.Field))


def test_register_field__django_field_instance(type_registry: TypeRegistry):
    with pytest.raises(AssertionError):
        type_registry.register(models.Field(), mock.Mock(spec=slothql.Field))


def test_clear(type_registry: TypeRegistry):
    type_registry._type_mapping = {'field': 'whatever'}
    type_registry.clear()
    assert type_registry._type_mapping == {}


def test_unregister(type_registry: TypeRegistry):
    type_registry._type_mapping = {'field': 'whatever', 'field2': 'wtf'}
    type_registry.unregister('field')
    assert type_registry._type_mapping == {'field2': 'wtf'}


def test_get(type_registry: TypeRegistry):
    type_registry._type_mapping = {'field': 'whatever', str: 'wtf'}
    assert type_registry.get('field2') == 'wtf'


def test_get__not_supported(type_registry: TypeRegistry):
    type_registry._type_mapping = {bool: True, str: 'wtf'}
    with pytest.raises(NotImplementedError):
        type_registry.get(42)

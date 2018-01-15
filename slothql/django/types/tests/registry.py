import pytest
from unittest import mock

from django.db import models

import slothql

from ..registry import TypeRegistry


def test_singleton():
    assert id(TypeRegistry()) == id(TypeRegistry())


def test_register_field():
    field = mock.Mock(spec=slothql.Field)
    TypeRegistry().register(models.Field, field)
    assert TypeRegistry()._type_mapping[models.Field] == field


def test_register_field__invalid_django_field():
    with pytest.raises(AssertionError):
        TypeRegistry().register(models.Model, mock.Mock(spec=slothql.Field))


def test_register_field__django_field_instance():
    with pytest.raises(AssertionError):
        TypeRegistry().register(models.Field(), mock.Mock(spec=slothql.Field))


def test_clear():
    TypeRegistry()._type_mapping = {'field': 'whatever'}
    TypeRegistry().clear()
    assert TypeRegistry()._type_mapping == {}


def test_unregister():
    TypeRegistry()._type_mapping = {'field': 'whatever', 'field2': 'wtf'}
    TypeRegistry().unregister('field')
    assert TypeRegistry()._type_mapping == {'field2': 'wtf'}


def test_get():
    TypeRegistry()._type_mapping = {'field': 'whatever', str: 'wtf'}
    assert TypeRegistry().get('field2') == 'wtf'


def test_get__not_supported():
    TypeRegistry()._type_mapping = {bool: True, str: 'wtf'}
    with pytest.raises(NotImplementedError):
        TypeRegistry().get(42)

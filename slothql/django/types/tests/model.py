from ..model import Model

import pytest
from unittest import mock

from django.db import models

import slothql

from ..registry import TypeRegistry


def test_is_abstract():
    assert Model._meta.abstract


def test_model__missing_meta():
    with pytest.raises(AssertionError) as exc_info:
        class Example(Model):
            pass
    assert f'class Example is missing "Meta" class' == str(exc_info.value)


def test_model__missing_model():
    with pytest.raises(AssertionError) as exc_info:
        class Example(Model):
            class Meta:
                pass
    assert f'"model" is required for object ModelOptions'


def test_model__model_not_registered():
    class NotRegistered(models.Model):
        class Meta:
            app_label = 'slothql.tests'

    class Example(Model):
        class Meta:
            abstract = True
            model = NotRegistered


def test_model__abstract_model():
    class Abstract(models.Model):
        class Meta:
            abstract = True
            app_label = 'slothql.tests'

    class Example(Model):
        class Meta:
            abstract = True
            model = Abstract


def test_fields__regular():
    class ModelAttrsRegular(models.Model):
        field = models.TextField()

        class Meta:
            app_label = 'slothql.tests'

    field_mock = mock.Mock(spec=slothql.Field)
    with mock.patch.object(TypeRegistry, 'get', return_value=field_mock) as get:  # type: mock.MagicMock
        class Type(Model):
            class Meta:
                model = ModelAttrsRegular
                fields = ('field',)

    (field,), kwargs = get.call_args
    assert isinstance(field, models.TextField) and field.name == 'field'
    assert Type._meta.fields == {'field': field_mock}

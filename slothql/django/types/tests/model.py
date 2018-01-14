from ..model import Model

import pytest
from unittest import mock

from django.db import models


def test_is_abstract():
    assert Model._meta.abstract


def test_model__missing_meta():
    with pytest.raises(AssertionError) as exc_info:
        class Example(Model):
            pass
    assert f'class Example is missing Meta class' == str(exc_info.value)


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
            model = NotRegistered


def test_model__abstract_model():
    class Abstract(models.Model):
        class Meta:
            abstract = True
            app_label = 'slothql.tests'

    class Example(Model):
        class Meta:
            model = Abstract


class ExampleModel(models.Model):
    field = models.TextField()

    def method_field(self):
        return f'method: {self.field}'

    @property
    def property_field(self):
        return f'property: {self.field}'

    class Meta:
        app_label = 'slothql.tests'


class TestModel:
    @classmethod
    def setup_class(cls):
        class Example(Model):
            class Meta:
                model = ExampleModel
                fields = ('',)

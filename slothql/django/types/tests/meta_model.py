import pytest

from django.db import models

from ..model import Model


def test_model__missing_model():
    with pytest.raises(AssertionError) as exc_info:
        class Example(Model):
            class Meta:
                pass
    assert f'"model" is required for object ModelOptions'


def test_model__model_not_registered():
    class NotRegistered(models.Model):
        class Meta:
            app_label = 'slothql'

    class Example(Model):
        class Meta:
            abstract = True
            model = NotRegistered


def test_model__abstract_model():
    class Abstract(models.Model):
        class Meta:
            abstract = True
            app_label = 'slothql'

    class Example(Model):
        class Meta:
            abstract = True
            model = Abstract

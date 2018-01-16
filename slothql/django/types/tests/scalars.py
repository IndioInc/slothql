import pytest

from django.db import models

import slothql

from ..registry import TypeRegistry


@pytest.mark.parametrize('django_field, expected_class', (
        (models.AutoField(), slothql.Integer),
        (models.BigAutoField(), slothql.Integer),

        (models.IntegerField(), slothql.Integer),
        (models.BigIntegerField(), slothql.Integer),
        (models.PositiveIntegerField(), slothql.Integer),
        (models.SmallIntegerField(), slothql.Integer),
        (models.PositiveSmallIntegerField(), slothql.Integer),

        (models.CharField(), slothql.String),
        (models.TextField(), slothql.String),
        (models.EmailField(), slothql.String),

        (models.BooleanField(), slothql.Boolean),
        (models.NullBooleanField(), slothql.Boolean),

        (models.FloatField(), slothql.Float),
        (models.DecimalField(), slothql.Float),

        (models.DateTimeField(), slothql.DateTime),
        (models.DateField(), slothql.Date),
        (models.TimeField(), slothql.Time),
))
def test_registered(django_field, expected_class):
    assert isinstance(TypeRegistry().get(django_field), expected_class)

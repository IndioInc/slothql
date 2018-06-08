import pytest

from django.contrib.postgres import fields

import slothql

from ..registry import TypeRegistry


@pytest.mark.parametrize(
    "django_field, expected_class", ((fields.JSONField(), slothql.JsonString),)
)
def test_registered(django_field, expected_class):
    assert isinstance(TypeRegistry().get(django_field), expected_class)

import pytest
from unittest import mock

from django.db import models

import slothql

from ..model import Model
from ..registry import TypeRegistry


class MetaFieldsModel(models.Model):
    field = models.TextField()
    related = models.ForeignKey('self', models.CASCADE)

    class Meta:
        app_label = 'slothql'


def test_fields__regular():
    field_mock = mock.Mock(spec=slothql.Field)
    with mock.patch.object(TypeRegistry, 'get', return_value=field_mock) as get:
        class Test(Model):
            class Meta:
                model = MetaFieldsModel
                fields = ('field',)

    (field,), kwargs = get.call_args
    assert isinstance(field, models.TextField) and field.name == 'field'
    assert {'field': field_mock} == Test._meta.fields


@pytest.mark.parametrize('declared_fields, exc_message', (
        (('invalid',), '"invalid" is not a valid field for model "MetaFieldsModel"'),
        (('related',), '"related" has to be declared explicitly, to avoid type collisions'),
))
def test_invalid_field(declared_fields, exc_message):
    with pytest.raises(AssertionError) as exc_info:
        class Test(Model):
            class Meta:
                model = MetaFieldsModel
                fields = declared_fields
    assert exc_message == str(exc_info.value)


def test_fields__all__(field_mock):
    with mock.patch.object(TypeRegistry, 'get', return_value=field_mock):
        class Test(Model):
            class Meta:
                model = MetaFieldsModel
                fields = '__all__'

    assert {'id': field_mock, 'field': field_mock} == Test._meta.fields

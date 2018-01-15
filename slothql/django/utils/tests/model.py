import pytest

from django.db import models

from ..model import get_model_attrs


def test_get_model_attrs__regular_field():
    class ModelAttrsField(models.Model):
        field = models.TextField()

        class Meta:
            app_label = 'slothql.tests'

    attrs = get_model_attrs(ModelAttrsField)
    del attrs['id']  # noqa
    assert attrs.keys() == {'field'} and isinstance(attrs.get('field'), models.TextField)


@pytest.mark.skip(reason='not implemented yet')
def test_get_model_attrs__method_field():
    class ModelAttrsMethod(models.Model):
        def method_field(self):
            return f'method'

        class Meta:
            app_label = 'slothql.tests'

    assert get_model_attrs(ModelAttrsMethod) == {'method_field': ModelAttrsMethod.method_field}


@pytest.mark.skip(reason='not implemented yet')
def test_get_model_attrs__property_field():
    class ModelAttrsProperty(models.Model):
        @property
        def property_field(self):
            return f'property'

        class Meta:
            app_label = 'slothql.tests'

    assert get_model_attrs(ModelAttrsProperty) == {'property_field': ModelAttrsProperty.property_field}

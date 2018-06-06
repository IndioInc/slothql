from django.db import models

import pytest

import slothql


def test_is_abstract():
    assert slothql.django.Model._meta.abstract


def test_model__missing_meta():
    with pytest.raises(AssertionError) as exc_info:
        class Example(slothql.django.Model):
            pass
    assert f'class Example is missing "Meta" class' == str(exc_info.value)


def test_relation_field_validation():
    class FooModel(models.Model):
        class Meta:
            app_label = 'slothql'

    class Foo(slothql.django.Model):
        foo = models.Field(lambda: Foo)

        class Meta:
            model = FooModel
            fields = '__all__'

    class Query(slothql.Object):
        foo = slothql.Field(lambda: Foo)

    with pytest.raises(AssertionError) as exc_info:
        slothql.Schema(query=Query)
    assert '' == str(exc_info.value)

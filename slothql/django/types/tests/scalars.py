from typing import Type

from django.db import models

import slothql
import slothql.django

from ..registry import TypeRegistry


def _model_factory(django_field: models.Field):
    class Model(models.Model):
        field = django_field

        class Meta:
            app_label = 'slothql.tests'

    Model.__name__ = f'{type(django_field).__name__}Model'
    return Model


def _model_type_factory(model_: Type[models.Model]):
    class ModelType(slothql.django.Model):
        class Meta:
            model = model_
            fields = ('field',)

    return ModelType


def _schema_factory(query_field: slothql.Field):
    class Query(slothql.Object):
        model = query_field

    return slothql.Schema(query=Query)


class TestCharField:
    def test_registered(self):
        assert isinstance(TypeRegistry().get(models.CharField()), slothql.String)

    def test_integration(self):
        model, resolver = _model_factory(models.TextField()), lambda *_: model(field='foo')
        schema = _schema_factory(slothql.Field(_model_type_factory(model), resolver))
        assert {'data': {'model': {'field': 'foo'}}} == slothql.gql(schema, 'query { model { field } }')


class TestTextField:
    def test_registered(self):
        assert isinstance(TypeRegistry().get(models.TextField()), slothql.String)

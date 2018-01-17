import pytest

import slothql
import slothql.django

from django.db import models


class ModelA(models.Model):
    field = models.TextField()

    class Meta:
        app_label = 'slothql'


class ModelB(models.Model):
    field = models.TextField()
    a = models.ManyToManyField(ModelA)

    class Meta:
        app_label = 'slothql'


class A(slothql.django.Model):
    class Meta:
        model = ModelA
        fields = '__all__'


class B(slothql.django.Model):
    # a = slothql.Field(A)

    class Meta:
        model = ModelB
        fields = '__all__'


class Query(slothql.Object):
    a = slothql.Field(A)
    b = slothql.Field(B)


schema = slothql.Schema(query=Query)


def test_nested_model_query():
    slothql.gql(schema, 'query { b { a { field } }')

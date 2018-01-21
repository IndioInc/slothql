import pytest
from unittest import mock

from django.db import models

import slothql

from ..model import Model


class RelationParent(models.Model):
    field = models.TextField()

    class Meta:
        app_label = 'slothql'


class RelationChild(models.Model):
    parent = models.ForeignKey(RelationParent, models.CASCADE, related_name='children')
    field = models.TextField()

    class Meta:
        app_label = 'slothql'


class Child(Model):
    class Meta:
        model = RelationChild
        fields = '__all__'


class Parent(Model):
    children = slothql.Field(Child, many=True)

    class Meta:
        model = RelationParent
        fields = '__all__'


@pytest.mark.xfail(reason='needs research')
def test_relation(info):
    manager = mock.Mock(models.Manager, get_queryset=[1, 2, 3])
    parent = mock.Mock(spec=Parent, children=manager)
    assert [1, 2, 3] == Parent.children.resolver(parent, info(field_name='children'))

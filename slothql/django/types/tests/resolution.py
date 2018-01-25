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


def test_resolve__relation(info):
    manager = mock.Mock(models.Manager)
    manager.get_queryset.return_value = [1, 2, 3]
    parent = mock.Mock(spec=Parent, children=manager)
    assert [1, 2, 3] == Parent.children.resolver(parent, info(field_name='children'))


def test_resolve__default(info):
    with mock.patch.object(Child._meta.model._default_manager, 'get_queryset', return_value=[1, 2, 3]) as get_queryset:
        assert [1, 2, 3] == Parent.children.resolver(None, info(field_name='children'))
        get_queryset.assert_called_with()

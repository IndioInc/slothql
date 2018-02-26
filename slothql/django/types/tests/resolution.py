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


def test_resolve__relation(info_mock, manager_mock, queryset_mock):
    manager_mock.get_queryset.return_value = queryset_mock
    parent = mock.Mock(spec=Parent, children=manager_mock)
    assert queryset_mock.filter() == Parent.children.resolver(parent, info_mock(field_name='children'))


def test_resolve__default(info_mock, queryset_mock):
    model = Child._meta.model
    with mock.patch.object(model._default_manager, 'get_queryset', return_value=queryset_mock) as get_queryset:
        assert queryset_mock.filter() == Parent.children.resolver(None, info_mock(field_name='children'))
        get_queryset.assert_called_with()

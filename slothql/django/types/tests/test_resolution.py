import pytest
from unittest import mock

from django.db import models

import slothql

from ..model import Model


class TestResolution:
    @classmethod
    def setup_class(cls):
        class RelationParent(models.Model):
            field = models.TextField()

            class Meta:
                app_label = "slothql"

        cls.RelationParent = RelationParent

        class RelationChild(models.Model):
            parent = models.ForeignKey(
                RelationParent, models.CASCADE, related_name="children"
            )
            field = models.TextField()

            class Meta:
                app_label = "slothql"

        cls.RelationChild = RelationChild

        class Child(Model):
            class Meta:
                model = RelationChild
                fields = "__all__"

        cls.Child = Child

        class Parent(Model):
            children = slothql.Field(Child, many=True)

            class Meta:
                model = RelationParent
                fields = "__all__"

        cls.Parent = Parent

    @pytest.mark.xfail
    def test_resolve__relation(self, info_mock, manager_mock, queryset_mock):
        manager_mock.get_queryset.return_value = queryset_mock
        parent = mock.Mock(spec=self.Parent, children=manager_mock)
        assert queryset_mock.filter() == self.Parent.children.resolver(
            parent, info_mock(field_name="children")
        )

    @pytest.mark.xfail
    def test_resolve__default(self, info_mock, queryset_mock):
        model = self.Child._meta.model
        with mock.patch.object(
            model._default_manager, "get_queryset", return_value=queryset_mock
        ) as get_queryset:
            assert queryset_mock.filter() == self.Parent.children.resolver(
                None, info_mock(field_name="children")
            )
            get_queryset.assert_called_with()

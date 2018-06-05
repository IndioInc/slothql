import typing as t
from unittest import mock

import pytest

from django.db import models

import slothql


class TestNestedFilters:
    @classmethod
    def setup_class(cls):
        class FooModel(models.Model):
            class Meta:
                app_label = 'slothql'

        class BarModel(models.Model):
            foo = models.OneToOneField(FooModel, models.CASCADE)

            class Meta:
                app_label = 'slothql'

        class Foo(slothql.django.Model):
            bars = slothql.Field(lambda: Bar, many=True)

            class Meta:
                model = FooModel
                fields = '__all__'

        class Bar(slothql.django.Model):
            foo = slothql.Field(Foo)

            class Meta:
                model = BarModel
                fields = '__all__'

        class Query(slothql.Object):
            bars = slothql.Field(Bar, many=True)
            foos = slothql.Field(Foo, many=True)

        cls.FooModel = FooModel
        cls.BarModel = BarModel
        cls.Foo = Foo
        cls.Bar = Bar
        cls.Query = Query
        cls.schema = slothql.Schema(query=cls.Query)

    def test_references(self):
        filter_class: t.Type[slothql.django.DjangoFilter] = self.Bar.filter_class
        assert issubclass(filter_class, slothql.django.DjangoFilter)
        assert {'foo', 'id'} == filter_class._meta.fields.keys()

        nested_filter_class = filter_class._meta.fields.get('foo').of_type
        assert nested_filter_class is self.Foo.filter_class

    def test_select_related(self, queryset_factory):
        queryset = queryset_factory(model=self.BarModel)
        with mock.patch.object(self.BarModel._default_manager, 'get_queryset', return_value=queryset):
            slothql.gql(self.schema, 'query { bars { foo { id } } }')

        queryset.select_related.assert_called_once_with('foo')

    def test_filter(self, queryset_factory):
        queryset = queryset_factory(model=self.BarModel)
        with mock.patch.object(self.BarModel._default_manager, 'get_queryset', return_value=queryset):
            slothql.gql(self.schema, 'query { bars(filter: {id: 1}) { foo { id } } }')

        queryset.filter.assert_called_once_with(id=1)

    @pytest.mark.xfail
    def test_prefetch_related(self, queryset_factory):
        queryset = queryset_factory(model=self.FooModel)
        with mock.patch.object(self.FooModel._default_manager, 'get_queryset', return_value=queryset):
            slothql.gql(self.schema, 'query { foos { bars { id } } }')

        queryset.prefetch_related.assert_called_once_with(
            models.Prefetch('bars', queryset=self.FooModel._default_manager.get_queryset())
        )

    @pytest.mark.xfail
    def test_prefetch_related_with_filter(self, queryset_factory):
        queryset = queryset_factory(model=self.FooModel)
        with mock.patch.object(self.FooModel._default_manager, 'get_queryset', return_value=queryset):
            slothql.gql(self.schema, 'query { foos { bars(filter: {id: 1}) { id } } }')

        queryset.prefetch_related.assert_called_once_with()

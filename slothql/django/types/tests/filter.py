import typing as t

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
            class Meta:
                model = FooModel
                fields = '__all__'

        class Bar(slothql.django.Model):
            foo = slothql.Field(Foo)

            class Meta:
                model = BarModel
                fields = '__all__'

        cls.Foo = Foo
        cls.Bar = Bar

    def test_references(self):
        filter_class: t.Type[slothql.django.DjangoFilter] = self.Bar.filter_class
        assert issubclass(filter_class, slothql.django.DjangoFilter)
        assert {'foo', 'id'} == filter_class._meta.fields.keys()

        nested_filter_class = filter_class._meta.fields.get('foo').of_type
        assert nested_filter_class is self.Foo.filter_class

import inspect
import typing as t

import pytest

import slothql
from .. import filter


def test_create_class():
    class FooFilter(filter.Filter):
        string_field = slothql.String()
        float_field = slothql.Float()

    assert "FooFilter" == FooFilter._meta.name
    assert {
        "string_field": FooFilter.string_field,
        "float_field": FooFilter.float_field,
    } == FooFilter._meta.fields


def test_create_class_inline():
    FooFilter = filter.Filter.create_class(
        name="FooFilter",
        fields={"string_field": slothql.String(), "float_field": slothql.Float()},
    )

    assert inspect.isclass(FooFilter) and issubclass(FooFilter, filter.Filter)
    assert "FooFilter" == FooFilter._meta.name
    assert {
        "string_field": FooFilter.string_field,
        "float_field": FooFilter.float_field,
    } == FooFilter._meta.fields


def test_filter_meta():
    class FooFilter(filter.Filter):
        class Meta:
            name = "BazFilter"
            description = "custom description"

    assert ("BazFilter", "custom description") == (
        FooFilter._meta.name,
        FooFilter._meta.description,
    )


def test_filter_meta_inline():
    FooFilter = filter.Filter.create_class(
        name="BazFilter", fields={}, description="custom description"
    )

    assert ("BazFilter", "custom description") == (
        FooFilter._meta.name,
        FooFilter._meta.description,
    )


class TestInitializeFilter:
    @classmethod
    def setup_class(cls):
        class FooFilter(filter.Filter):
            string_field = slothql.String()
            float_field = slothql.Float()

        cls.FooFilter = FooFilter

    def test_full_initialize(self):
        foo_filter = self.FooFilter(string_field="string", float_field=12.23)
        assert ("string", 12.23) == (foo_filter.string_field, foo_filter.float_field)

    def test_partial_initialize(self):
        foo_filter = self.FooFilter(float_field=12.23)
        assert (filter.Filter.SKIP, 12.23) == (
            foo_filter.string_field,
            foo_filter.float_field,
        )

    def test_empty_initialize(self):
        foo_filter = self.FooFilter()
        assert (filter.Filter.SKIP, filter.Filter.SKIP) == (
            foo_filter.string_field,
            foo_filter.float_field,
        )

    def test_invalid_initialize(self):
        with pytest.raises(TypeError) as exc_info:
            self.FooFilter(invalid=12)
        assert (
            "FooFilter.__init__() got an unexpected keyword argument 'invalid'"
            == str(exc_info.value)
        )


def test_nested_filters():
    class Foo(slothql.Object):
        id = slothql.ID()

    class Bar(slothql.Object):
        id = slothql.ID()
        foo = slothql.Field(Foo)

    filter_class: t.Type[filter.Filter] = Bar.filter_class
    assert issubclass(filter_class, filter.Filter)
    assert {"foo", "id"} == filter_class._meta.fields.keys()

    nested_filter_class = filter_class._meta.fields.get("foo").of_type
    assert nested_filter_class is Foo.filter_class


def test_duplicate_references():
    class Foo(slothql.Object):
        id = slothql.ID()

    class Bar(slothql.Object):
        foo_one = slothql.Field(Foo)
        foo_two = slothql.Field(Foo)

    foo_one_filter_cls, foo_two_filter_cls = [
        f.of_type for f in Bar.filter_class._meta.fields.values()
    ]
    assert foo_one_filter_cls is foo_two_filter_cls

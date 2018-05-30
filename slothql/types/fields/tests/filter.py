import inspect

import slothql
from .. import filter


def test_create_class():
    class FooFilter(filter.Filter):
        string_field = slothql.String()
        float_field = slothql.Float()

    assert 'FooFilter' == FooFilter._meta.name
    assert {
               'string_field': FooFilter.string_field,
               'float_field': FooFilter.float_field,
           } == FooFilter._meta.fields


def test_create_class_inline():
    FooFilter = filter.Filter.create_class(name='FooFilter', fields={
        'string_field': slothql.String(),
        'float_field': slothql.Float(),
    })

    assert inspect.isclass(FooFilter) and issubclass(FooFilter, filter.Filter)
    assert 'FooFilter' == FooFilter._meta.name
    assert {
               'string_field': FooFilter.string_field,
               'float_field': FooFilter.float_field,
           } == FooFilter._meta.fields


def test_filter_meta():
    class FooFilter(filter.Filter):
        class Meta:
            name = 'BazFilter'
            description = 'custom description'

    assert ('BazFilter', 'custom description') == (FooFilter._meta.name, FooFilter._meta.description)


def test_filter_meta_inline():
    FooFilter = filter.Filter.create_class(name='BazFilter', fields={}, description='custom description')

    assert ('BazFilter', 'custom description') == (FooFilter._meta.name, FooFilter._meta.description)


class TestInitializeFilter:
    @classmethod
    def setup_class(cls):
        class FooFilter(filter.Filter):
            string_field = slothql.String()
            float_field = slothql.Float()

        cls.FooFilter = FooFilter

    def test_full_initialize(self):
        foo_filter = self.FooFilter(string_field='string', float_field=12.23)
        assert ('string', 12.23) == (foo_filter.string_field, foo_filter.float_field)

    def test_partial_initialize(self):
        foo_filter = self.FooFilter(float_field=12.23)
        assert (filter.Filter.SKIP, 12.23) == (foo_filter.string_field, foo_filter.float_field)

    def test_empty_initialize(self):
        foo_filter = self.FooFilter()
        assert (filter.Filter.SKIP, filter.Filter.SKIP) == (foo_filter.string_field, foo_filter.float_field)

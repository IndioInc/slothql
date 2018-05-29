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

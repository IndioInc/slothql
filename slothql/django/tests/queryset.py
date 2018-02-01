import pytest
from unittest import mock

from django.db import models

from ..queryset import get_optimized_queryset, remove_selections


class Foo(models.Model):
    foos = models.ManyToManyField('self', related_name='foos')
    field = models.TextField()

    class Meta:
        app_label = 'slothql'


class Bar(models.Model):
    bar = models.ForeignKey('self', models.CASCADE, related_name='bars')
    foo = models.ForeignKey(Foo, models.CASCADE, related_name='bars')
    field = models.TextField()

    class Meta:
        app_label = 'slothql'


@mock.patch.object(Bar._default_manager, 'get_queryset')
def test_0_depth(get_queryset: mock.MagicMock):
    assert get_queryset.return_value == get_optimized_queryset(Bar._default_manager, {'field': None})
    get_queryset.return_value.select_related.assert_not_called()
    get_queryset.return_value.prefetch_related.assert_not_called()


@pytest.mark.parametrize('selections, select', (
        ({'bar': {'field': None}}, ('bar',)),
        ({'bar': {'bar': {'field': None}}}, ('bar__bar',)),
        ({'bar': {'foo': {'field': None}}}, ('bar__foo',)),
        ({'foo': {'field': None}, 'bar': {'foo': {'field': None}}}, ('foo', 'bar__foo',)),
))
@mock.patch.object(Bar._default_manager, 'get_queryset')
def test_select(get_queryset, selections, select):  # FIXME: temporary prefetching everything
    prefetch_related = get_queryset.return_value.prefetch_related
    assert prefetch_related.return_value == get_optimized_queryset(Bar._default_manager, selections)
    prefetch_related.assert_called_once_with(*select)
    get_queryset.select_related.assert_not_called()


@pytest.mark.parametrize('input_selections, selects, exoected', (

))
def test_remove_selections(input_selections, selects, exoected):
    assert exoected == remove_selections(input_selections, selects)


@pytest.mark.parametrize('selections, prefetch', (
        ({'bars': {'field': None}}, ('bars',)),
))
@mock.patch.object(Foo._default_manager, 'get_queryset')
def test_prefetch(get_queryset, selections, prefetch):
    prefetch_related = get_queryset.return_value.prefetch_related
    assert prefetch_related.return_value == get_optimized_queryset(Foo._default_manager, selections)
    prefetch_related.assert_called_once_with(*prefetch)
    get_queryset.select_related.assert_not_called()

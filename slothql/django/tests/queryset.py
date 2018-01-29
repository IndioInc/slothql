import pytest
from unittest import mock

from django.db import models
from django.db.models import Prefetch

from ..queryset import get_optimized_queryset, remove_selections


class Foo(models.Model):
    foos = models.ManyToManyField('self')
    field = models.TextField()

    class Meta:
        app_label = 'slothql'


class Bar(models.Model):
    bar = models.ForeignKey('self', models.CASCADE)
    foo = models.ForeignKey(Foo, models.CASCADE)
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
def test_select(get_queryset, selections, select):
    select_related = get_queryset.return_value.select_related
    assert select_related.return_value == get_optimized_queryset(Bar._default_manager, selections)
    select_related.assert_called_once_with(*select)
    get_queryset.prefetch_related.assert_not_called()



@pytest.mark.parametrize('input_selections, selects, exoected', (

))
def test_remove_selections(input_selections, selects, exoected):
    assert exoected == remove_selections(input_selections, selects)

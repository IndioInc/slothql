import pytest
from unittest import mock

from django.db import models


@pytest.fixture()
def manager(**kwargs):
    return mock.Mock(spec=models.Manager, get_queryset=mock.Mock(side_effect=queryset))


@pytest.fixture()
def model(model_class=None, **kwargs):
    default_manager = manager()
    return mock.Mock(
        spec=model_class or models.Model,
        _default_manager=default_manager,
        objects=default_manager,
    )


@pytest.fixture()
def queryset(**kwargs):
    model_class = kwargs.pop("model", None)
    model_instance = model(model_class=model_class)
    queryset_instance = mock.Mock(
        spec=models.QuerySet,
        side_effect=queryset,
        get=mock.Mock(side_effect=lambda: model()),
        select_related=mock.Mock(side_effect=lambda *_: queryset_instance),
        prefetch_related=mock.Mock(side_effect=lambda *_: queryset_instance),
        filter=mock.Mock(side_effect=lambda **_: queryset_instance),
        __iter__=lambda self: iter((model_instance, model_instance, model_instance)),
        _iterable_class=models.query.ModelIterable,
        model=model_class,
        **kwargs,
    )
    return queryset_instance


@pytest.fixture()
def queryset_factory():
    return queryset

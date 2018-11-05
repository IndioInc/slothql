from unittest import mock
import typing as t

from django.db import models


def mock_manager():
    return mock.Mock(
        spec=models.Manager, get_queryset=mock.Mock(side_effect=mock_queryset)
    )


def mock_model(model_class: t.Type[models.Model]):
    manager = mock_manager()
    return mock.Mock(spec=model_class, _default_manager=manager, objects=manager)


def mock_queryset(model_class: t.Type[models.Model], **kwargs):
    model_instance = mock_model(model_class)()
    queryset_instance = mock.Mock(
        spec=models.QuerySet,
        side_effect=mock_queryset,
        get=mock.Mock(side_effect=lambda: model_instance),
        select_related=mock.Mock(side_effect=lambda *_: queryset_instance),
        prefetch_related=mock.Mock(side_effect=lambda *_: queryset_instance),
        filter=mock.Mock(side_effect=lambda **_: queryset_instance),
        __iter__=lambda self: iter((model_instance, model_instance, model_instance)),
        _iterable_class=models.query.ModelIterable,
        model=model_class,
        **kwargs,
    )
    return queryset_instance

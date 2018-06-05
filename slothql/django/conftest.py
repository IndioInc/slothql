import pytest
from unittest import mock

from django.db import models


def queryset(**kwargs):
    queryset_instance = mock.Mock(
        spec=models.QuerySet,
        side_effect=queryset,
        select_related=mock.Mock(side_effect=lambda *_: queryset_instance),
        prefetch_related=mock.Mock(side_effect=lambda *_: queryset_instance),
        filter=mock.Mock(side_effect=lambda **_: queryset_instance),
        __iter__=lambda self: iter(()),
        **kwargs,
    )
    return queryset_instance


@pytest.fixture()
def queryset_factory():
    return queryset

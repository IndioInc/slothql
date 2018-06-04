import pytest
from unittest import mock

from django.db import models


@pytest.fixture()
def queryset():
    return mock.Mock(spec=models.QuerySet, side_effect=queryset, __iter__=lambda self: iter(()))

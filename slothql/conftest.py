import pytest
from unittest import mock

import django
from django.conf import settings
from django.db import models

import graphql
from graphql.type.definition import GraphQLType

import slothql
from slothql.types.base import BaseType


def pytest_configure():
    settings.configure()
    django.setup()


# setup for @pytest.mark.incremental

def pytest_runtest_makereport(item, call):
    if 'incremental' in item.keywords:
        if call.excinfo is not None and not item._skipped_by_mark:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if 'incremental' in item.keywords:
        previousfailed = getattr(item.parent, '_previousfailed', None)
        if previousfailed is not None:
            pytest.xfail(f'previous test failed ({previousfailed.name})')


@pytest.fixture()
def type_mock():
    return lambda: BaseType(mock.Mock(spec=GraphQLType))


@pytest.fixture()
def info_mock():
    return lambda **kwargs: mock.Mock(spec=graphql.ResolveInfo, **kwargs)


@pytest.fixture()
def resolver_mock():
    return mock.Mock(side_effect=lambda o, *_: o)


@pytest.fixture()
def field_mock():
    return mock.Mock(spec=slothql.Field)


@pytest.fixture()
def partials_equal():
    return lambda p1, p2: p1.func == p2.func and p1.args == p2.args and p1.keywords == p2.keywords


@pytest.fixture()
def manager_mock():
    return mock.Mock(spec=models.Manager)


@pytest.fixture()
def queryset_mock():
    return mock.Mock(spec=models.QuerySet)


@pytest.fixture()
def schema_mock():
    return mock.Mock(spec=slothql.Schema)


@pytest.fixture()
def operation_mock():
    return mock.Mock(spec=slothql.Operation, query='foo', variables={}, operation_name='baz')


@pytest.fixture()
def hello_schema():
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda: 'world')

    return slothql.Schema(query=Query)

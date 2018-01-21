import pytest
from unittest import mock

import django
from django.conf import settings

import graphql
from graphql.type.definition import GraphQLType

import slothql


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
def type():
    return lambda: mock.Mock(spec=GraphQLType)


@pytest.fixture()
def info():
    return lambda **kwargs: mock.Mock(spec=graphql.ResolveInfo, **kwargs)


@pytest.fixture()
def resolver_mock():
    return mock.Mock(side_effect=lambda o, *_: o)


@pytest.fixture()
def field_mock(type):
    return mock.Mock(spec=slothql.Field)


@pytest.fixture()
def partials_equal():
    return lambda p1, p2: p1.func == p2.func and p1.args == p2.args and p1.keywords == p2.keywords

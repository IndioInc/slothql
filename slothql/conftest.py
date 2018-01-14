import pytest
from unittest import mock

import graphql
from graphql.type.definition import GraphQLType


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
def resolver():
    return mock.Mock(side_effect=lambda o, *_: o)

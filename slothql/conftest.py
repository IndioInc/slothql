import pytest


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

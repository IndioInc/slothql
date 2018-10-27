import pytest

from contextlib import contextmanager


@contextmanager
def assert_exception(exception: Exception = None):
    if exception:
        with pytest.raises(type(exception)) as exc_info:
            yield
        assert exception == exc_info.value, f"{repr(exception)} != {exc_info.value}"
    else:
        yield

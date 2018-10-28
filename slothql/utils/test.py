import pytest

from contextlib import contextmanager


@contextmanager
def assert_exception(exception: Exception = None):
    if exception:
        with pytest.raises(type(exception)) as exc_info:
            yield
        assert str(exception) == str(
            exc_info.value
        ), f"{str(exception)} != {str(exc_info.value)}"
    else:
        yield

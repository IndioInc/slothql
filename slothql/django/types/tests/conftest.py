import pytest

from .test_registry import TypeRegistry


@pytest.fixture()
def type_registry():
    class TestTypeRegistry(TypeRegistry):
        pass
    return TestTypeRegistry()

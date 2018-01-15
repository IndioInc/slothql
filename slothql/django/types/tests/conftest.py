import pytest

from .registry import TypeRegistry


@pytest.fixture()
def type_registry():
    class TestTypeRegistry(TypeRegistry):
        pass
    return TestTypeRegistry()

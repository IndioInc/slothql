import copy

import pytest

from .registry import TypeRegistry


@pytest.fixture()
def type_registry():
    return copy.copy(TypeRegistry())

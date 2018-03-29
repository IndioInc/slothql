import pytest

from slothql.types.base import BaseType


@pytest.mark.parametrize('type_name, expected_name', (
        ('Foo', 'Foo'),
        (None, 'FooType'),
))
def test_meta_name(type_name, expected_name):
    class FooType(BaseType):
        class Meta:
            name = type_name

    assert expected_name == FooType()._meta.name

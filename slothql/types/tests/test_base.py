import pytest

from slothql.types.base import BaseType


@pytest.mark.parametrize(
    "type_name, expected_name", (("Foo", "Foo"), (None, "FooType"))
)
def test_meta_name(type_name, expected_name):
    class FooType(BaseType):
        class Meta:
            name = type_name

    assert expected_name == FooType._meta.name


def test_type_validation():
    with pytest.raises(AssertionError) as exc_info:

        class FooType(BaseType):
            class Meta:
                name = 12

    assert f"`name = 12` does not match type annotation `str`" == str(exc_info.value)

import pytest

from ..case import snake_to_camelcase, camelcase_to_snake


@pytest.mark.parametrize(
    "value, expected",
    (
        ("", ""),
        ("_", "_"),
        ("__", "__"),
        ("fooBar", "fooBar"),
        ("FooBar", "FooBar"),
        ("foo_bar_baz", "fooBarBaz"),
        ("foo__bar__baz", "foo_Bar_Baz"),
        ("_foo_bar_baz", "_fooBarBaz"),
        ("__foo_bar_baz", "__fooBarBaz"),
        ("foo_bar_baz_", "fooBarBaz_"),
        ("foo_bar_baz__", "fooBarBaz__"),
        ("_foo_bar_baz_", "_fooBarBaz_"),
        ("__foo_bar_baz__", "__fooBarBaz__"),
    ),
)
def test_snake_to_camelcase(value, expected):
    assert expected == snake_to_camelcase(value)


@pytest.mark.parametrize(
    "value, expected",
    (
        ("operation", "operation"),
        ("operationName", "operation_name"),
        ("OperationName", "operation_name"),
    ),
)
def test_camelcase_to_snake(value, expected):
    assert expected == camelcase_to_snake(value)

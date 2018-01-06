import pytest

from ..scalars import StringField


def test_string_field_init():
    StringField()


@pytest.mark.parametrize("value, expected", [
    ('123', '123'),
    (234, '234'),
    ({}, '{}'),
    ({'a': [1]}, "{'a': [1]}"),
])
def test_resolver_serialize(value, expected):
    assert expected == StringField.serialize(value)

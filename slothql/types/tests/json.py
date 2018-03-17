import pytest

from ..json import JsonStringType


@pytest.mark.parametrize('value, expected', (
        ('', '""'),
        (None, 'null'),
        (False, 'false'),
        (True, 'true'),
        ({}, '{}'),
        ([], '[]'),
        ((), '[]'),
        ({'k': 'v'}, '{"k": "v"}'),
        ({'k': ['v1', 'v2', 'v3']}, '{"k": ["v1", "v2", "v3"]}'),
        ({'k': {'v1'}}, '{"k": ["v1"]}'),
))
def test_serialize(value, expected):
    serialized = JsonStringType.serialize(value)
    assert expected == serialized and type(expected) is type(serialized)


@pytest.mark.parametrize('value', (
    object(),
    [object()],
))
def test_serialize__invalid( value):
    with pytest.raises(TypeError) as exc_info:
        JsonStringType.serialize(value)
    assert f'`{JsonStringType.__name__}.serialize` received invalid value {repr(value)}' == str(exc_info.value)

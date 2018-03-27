import pytest

from slothql.operation import Operation, OperationSyntaxError


@pytest.mark.parametrize('query, message', (
        ('abc', 'Invalid JSON: Expecting value: line 1 column 1 (char 0)'),
        (b'abc', 'Invalid JSON: Expecting value: line 1 column 1 (char 0)'),
        ("{'query': 'elo'}", 'Invalid JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)'),
))
def test_raw_query_invalid_json(query, message):
    with pytest.raises(OperationSyntaxError) as exc_info:
        Operation.from_string(query)
    assert message == str(exc_info.value)


@pytest.mark.parametrize('query', (
        '123',
        '[]',
        '"abc"',
        'NaN', '-Infinity', 'null',
        'true', 'false',
))
def test_raw_query__valid_json_invalid_type(query):
    with pytest.raises(OperationSyntaxError) as exc_info:
        Operation.from_string(query)
    assert str(exc_info.value) == 'GraphQL queries must a dictionary'


def test_raw_query__valid_json_missing_query():
    with pytest.raises(OperationSyntaxError) as exc_info:
        Operation.from_string('{"lol": "elo"}')
    assert str(exc_info.value) == '"query" not found in json object'


def test_raw_query__valid_query():
    Operation.from_string('{"query": "elo"}')

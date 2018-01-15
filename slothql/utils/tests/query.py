import pytest

from ..query import query_from_raw_json


@pytest.mark.parametrize('query', (
        'abc', b'abc',
        "{'query': 'elo'}",
))
def test_raw_query_invalid_json(query):
    with pytest.raises(ValueError) as exc_info:
        query_from_raw_json(query)
    assert str(exc_info.value).startswith('Expecting ')


@pytest.mark.parametrize('query', (
        '123',
        '[]',
        '"abc"',
        'NaN', '-Infinity', 'null',
        'true', 'false',
))
def test_raw_query__valid_json_invalid_type(query):
    with pytest.raises(ValueError) as exc_info:
        query_from_raw_json(query)
    assert str(exc_info.value) == 'GraphQL queries must a dictionary'


def test_raw_query__valid_json_missing_query():
    with pytest.raises(ValueError) as exc_info:
        query_from_raw_json('{"lol": "elo"}')
    assert str(exc_info.value) == '"query" not not found in json object'


def test_raw_query__valid_query():
    query_from_raw_json('{"query": "elo"}')

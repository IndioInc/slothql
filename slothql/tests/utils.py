import pytest

from .. import utils


def test_magic_name__magic_method():
    assert utils.is_magic_name('__foo__')


def test_magic_name__startswith_dunder():
    assert not utils.is_magic_name('__bar')


def test_magic_name__endswith_dunder():
    assert not utils.is_magic_name('baz__')


def test_magic_name__no_dunder():
    assert not utils.is_magic_name('papa')


def test_merge_object_dicts():
    class A:
        field_a = 'a'
        field_a_b = 'a'

    class B(A):
        field_a_b = 'b'
        field_b = 'b'

    assert utils.get_object_attributes(B) == {'field_a': 'a', 'field_a_b': 'b', 'field_b': 'b'}


@pytest.mark.parametrize('query', (
    'abc', b'abc',
    "{'query': 'elo'}",
))
def test_raw_query_invalid_json(query):
    with pytest.raises(ValueError) as exc_info:
        utils.raw_query_from_raw_json(query)
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
        utils.raw_query_from_raw_json(query)
    assert str(exc_info.value) == 'GraphQL queries must a dictionary'


def test_raw_query__valid_json_missing_query():
    with pytest.raises(ValueError) as exc_info:
        utils.raw_query_from_raw_json('{"lol": "elo"}')
    assert str(exc_info.value) == '"query" not not found in json object'


def test_raw_query__valid_query():
    utils.raw_query_from_raw_json('{"query": "elo"}')

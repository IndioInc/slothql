import pytest

import slothql

from ..query import gql


@pytest.mark.parametrize('query', (
        'query { hello }',
        '{ hello }',
))
def test_gql__valid_query(query):
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda *_: 'world')

    result = gql(slothql.Schema(query=Query), query)
    assert {'data': {'hello': 'world'}} == result


@pytest.mark.parametrize('query', (
        'query { hello ',
        'query { hell }',
))
def test_gql__syntax_error(query):
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda *_: 'world')

    result = gql(slothql.Schema(query=Query), query)
    assert result.get('errors')


@pytest.mark.xfail
def test_gql__exception_not_handled():
    def resolver(*_):
        raise RuntimeError

    class Query(slothql.Object):
        hello = slothql.String(resolver=resolver)

    with pytest.raises(RuntimeError):
        print(slothql.gql(slothql.Schema(query=Query), query='query { hello }'))


@pytest.mark.xfail
def test_multiple_operations():
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda: 'world')

    slothql.gql(slothql.Schema(query=Query), query='query q1 { hello } query q2 { hello }')

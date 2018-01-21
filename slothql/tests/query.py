import slothql

from ..query import gql


def test_q():
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda *_: 'world')

    result = gql(slothql.Schema(query=Query), 'query { hello }')
    assert result == {'data': {'hello': 'world'}}

import pytest

import slothql

from ..query import gql


def test_q():
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda *_: 'world')

    result = gql(slothql.Schema(query=Query), 'query { hello }')
    assert result == {'data': {'hello': 'world'}}


@pytest.mark.xfail
def test_q__exception_not_handled():
    def resolver(*_):
        raise RuntimeError

    class Query(slothql.Object):
        hello = slothql.String(resolver=resolver)

    with pytest.raises(RuntimeError):
        print(gql(slothql.Schema(query=Query), 'query { hello }'))

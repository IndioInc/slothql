import pytest

import slothql


@pytest.mark.xfail
@pytest.mark.parametrize('query, expected', (
        ('query { foos(id: 1) { id } }', [{'id': 1}]),
        ('query { foos(id: "1") { id } }', []),
        ('query { foos(id: {e: 1}) { id } }', [{'id': 1}]),
        ('query { foos(id: {in: [1, 2]}) { id } }', [{'id': 1}]),
))
def test_filtering(query, expected):
    class Foo(slothql.Object):
        id = slothql.ID()

    class Query(slothql.Object):
        foos = slothql.Field(Foo, resolver=lambda: [{'id': 1}, {'id': 2}, {'id': 3}], many=True)

    schema = slothql.Schema(query=Query)
    assert {'data': {'foos': expected}} == slothql.gql(schema, query)

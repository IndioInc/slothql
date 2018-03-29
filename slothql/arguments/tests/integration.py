import pytest

import slothql


@pytest.mark.parametrize('query, expected', (
        ('query { foos(id: 1) { id } }', [{'id': '1'}]),
        ('query { foos(id: "1") { id } }', [{'id': '1'}]),
        # ('query { foos(id: {eq: "1"}) { id } }', [{'id': '1'}]),
        # ('query { foos(id: {in: ["1", "2"]}) { id } }', [{'id': '1'}, {'id': '2'}]),
))
def test_filtering(query, expected):
    class Foo(slothql.Object):
        id = slothql.ID()

    class Query(slothql.Object):
        foos = slothql.Field(Foo, resolver=lambda: [{'id': '1'}, {'id': '2'}, {'id': '3'}], many=True)

    assert {'foos': expected} == slothql.gql(slothql.Schema(query=Query), query).data


def test_invalid_filter():
    class Foo(slothql.Object):
        id = slothql.ID()

    class Query(slothql.Object):
        foos = slothql.Field(Foo, many=True)

    error = {'message': 'Argument "id" has invalid value {wtf: 1}.\nExpected type "ID", found {wtf: 1}.'}
    assert [error] == slothql.gql(slothql.Schema(query=Query), 'query { foos(id: {wtf: 1}) { id } }').errors

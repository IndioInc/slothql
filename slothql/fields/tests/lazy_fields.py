import pytest

import slothql


@pytest.mark.skip(reason='not implemented yet')
def test_circular_dependency():
    class A(slothql.Object):
        b = slothql.Field('B')
        field = slothql.String()

    class B(slothql.Object):
        a = slothql.Field(A)
        field = slothql.String()

    class Query(slothql.Object):
        root = slothql.Field(A, resolver=lambda: {'b': {'a': {'field': 'foo'}}})

    schema = slothql.Schema(Query)

    query = 'query { root { b { a { field } } } }'
    assert {'data': {'root': {'b': {'a': {'field': 'foo'}}}}} == slothql.gql(schema, query)


@pytest.mark.skip(reason='not implemented yet')
@pytest.mark.parametrize('other', (
        ('A',),
        ('self',),
))
def test_self_dependency(other):
    class A(slothql.Object):
        a = slothql.Field(other)
        field = slothql.String()

    class Query(slothql.Object):
        root = slothql.Field(A, resolver=lambda: {'a': {'field': 'foo'}})

    schema = slothql.Schema(query=Query)

    query = 'query { root { a { field } } }'
    assert {'data': {'root': {'a': {'field': 'foo'}}}} == slothql.gql(schema, query)

import pytest

import slothql


def test_nested_model_query():
    class A(slothql.Object):
        field = slothql.String()

    class B(slothql.Object):
        a = slothql.Field(A)

    class Query(slothql.Object):
        def get_b(self, obj, info):
            return {'a': {'field': 'resolved'}}

        b = slothql.Field(B, resolver=get_b)

    schema = slothql.Schema(query=Query)

    assert {'data': {'b': {'a': {'field': 'resolved'}}}} == slothql.gql(schema, 'query { b { a { field } } }')


def test_duplicate_references():
    class A(slothql.Object):
        field = slothql.String()

    class Query(slothql.Object):
        a1 = slothql.Field(A)
        a2 = slothql.Field(A)

    slothql.Schema(query=Query)


@pytest.mark.parametrize('resolver, expected', (
        (lambda obj, info: [1, 2, 3], [1, 2, 3]),
        (None, None),
))
def test_list_field(resolver, expected):
    class Query(slothql.Object):
        list = slothql.Integer(resolver=resolver, many=True)

    schema = slothql.Schema(query=Query)

    assert {'data': {'list': expected}} == slothql.gql(schema, 'query { list }')


@pytest.mark.parametrize('query, expected', (
        ('query { foos(filter: {id: 1}) { id } }', [{'id': '1'}]),
        ('query { foos(filter: {id: "1"}) { id } }', [{'id': '1'}]),
        # ('query { foos(id: {eq: "1"}) { id } }', [{'id': '1'}]),
        # ('query { foos(id: {in: ["1", "2"]}) { id } }', [{'id': '1'}, {'id': '2'}]),
))
def test_filtering(query, expected):
    class Foo(slothql.Object):
        id = slothql.ID()

    class Query(slothql.Object):
        foos = slothql.Field(Foo, resolver=lambda: [{'id': '1'}, {'id': '2'}, {'id': '3'}], many=True, filterable=True)

    assert {'foos': expected} == slothql.gql(slothql.Schema(query=Query), query).data


def test_invalid_filter():
    class Foo(slothql.Object):
        id = slothql.ID()

    class Query(slothql.Object):
        foos = slothql.Field(Foo, many=True, filterable=True)

    error = {'message': 'Argument "filter" has invalid value {id: {wtf: 1}}.\n'
                        'In field "id": Expected type "ID", found {wtf: 1}.'}
    assert [error] == slothql.gql(slothql.Schema(query=Query), 'query { foos(filter: {id: {wtf: 1}}) { id } }').errors

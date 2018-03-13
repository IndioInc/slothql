import pytest

import slothql


@pytest.mark.xfail
def test_union_type():
    class A(slothql.Object):
        a = slothql.Field(slothql.Integer)

    class B(slothql.Object):
        b = slothql.Field(slothql.String)

    class Foo(slothql.Union):
        class Meta:
            types = (A, B)

    class Query(slothql.Object):
        foo = slothql.Field(Foo, many=True, resolver=lambda: [{'a': 1}, {'b': '2'}])

    schema = slothql.Schema(query=Query)
    assert {'data': {'foo': ['1', 2]}} == slothql.gql(schema, 'query { foo }')

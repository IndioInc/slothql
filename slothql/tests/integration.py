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


@pytest.mark.xfail
def test_q__exception_not_handled():
    def resolver(*_):
        raise RuntimeError

    class Query(slothql.Object):
        hello = slothql.String(resolver=resolver)

    with pytest.raises(RuntimeError):
        print(slothql.gql(slothql.Schema(query=Query), 'query { hello }'))

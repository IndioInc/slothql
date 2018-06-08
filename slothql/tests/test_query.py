import pytest

import slothql

from ..query import gql


@pytest.mark.parametrize(
    "kwargs, message",
    (
        ({"query": "foo"}, 'Using "query" with "operation" is ambiguous'),
        (
            {"variables": {"foo": "bar"}},
            'Using "variables" with "operation" is ambiguous',
        ),
        (
            {"operation_name": "foo"},
            'Using "operation_name" with "operation" is ambiguous',
        ),
    ),
)
def test_ambiguous_usage(schema_mock, operation_mock, kwargs, message):
    with pytest.raises(AssertionError) as exc_info:
        gql(schema_mock, **kwargs, operation=operation_mock)
    assert message == str(exc_info.value)


@pytest.mark.parametrize("query", ("query { hello }", "{ hello }"))
def test_gql__valid_query(query):
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda *_: "world")

    result = gql(slothql.Schema(query=Query), query)
    assert {"data": {"hello": "world"}} == result


@pytest.mark.parametrize("query", ("query { hello ", "query { hell }"))
def test_gql__syntax_error(query):
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda *_: "world")

    result = gql(slothql.Schema(query=Query), query)
    assert result.get("errors")


@pytest.mark.xfail
def test_gql__exception_not_handled():
    def resolver(*_):
        raise RuntimeError

    class Query(slothql.Object):
        hello = slothql.String(resolver=resolver)

    with pytest.raises(RuntimeError):
        print(slothql.gql(slothql.Schema(query=Query), query="query { hello }"))


@pytest.mark.xfail
def test_multiple_operations():
    class Query(slothql.Object):
        hello = slothql.String(resolver=lambda: "world")

    slothql.gql(
        slothql.Schema(query=Query), query="query q1 { hello } query q2 { hello }"
    )


@pytest.mark.xfail
def test_variables():
    class Foo(slothql.Object):
        bar = slothql.String()

    class Query(slothql.Object):
        def resolve_foo(self, obj, info, args):
            print(obj, info, args)
            return args

        foo = slothql.Field(Foo, resolver=resolve_foo)

    schema = slothql.Schema(query=Query)
    assert {"foo": "1"} == slothql.gql(
        schema, "query query($var: String) { foo(bar: $var) { bar } }", {"var": "1"}
    )

import pytest
import slothql


@pytest.mark.xfail
def test_schema_camelcase_integration():
    class FooBar(slothql.Object):
        some_weird_field = slothql.String(resolver=lambda: 'some weird field')

    class Query(slothql.Object):
        string_field = slothql.String(resolver=lambda: 'string field')
        foo_bar = slothql.Field(FooBar, resolver=lambda: {})

    schema = slothql.Schema(query=Query, auto_camelcase=True)
    assert {'data': {'stringField': 'string field', 'fooBar': {'someWeirdField': 'some weird field'}}} \
        == slothql.gql(schema, 'query { stringField fooBar { someWeirdField } }')

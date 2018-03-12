import pytest

import graphql

import slothql


class TestSchema:
    @classmethod
    def setup_class(cls):
        class Query(slothql.Object):
            hello = slothql.String(resolver=lambda *_: 'world')

        cls.query_class = Query

    def test_can_init(self):
        slothql.Schema(query=self.query_class())

    def test_can_init_with_callable_query(self):
        slothql.Schema(query=self.query_class)

    def test_execution(self):
        schema = slothql.Schema(query=self.query_class)
        query = 'query { hello }'
        assert {'data': {'hello': 'world'}} == slothql.gql(schema, query)

    @pytest.mark.parametrize('call', (True, False))
    def test_complex_schema(self, call):
        class Nested(slothql.Object):
            nested = slothql.Field(self.query_class() if call else self.query_class, lambda *_: {'world': 'not hello'})

        query = 'query { nested { hello } }'
        assert {'data': {'nested': {'hello': 'world'}}} == slothql.gql(slothql.Schema(query=Nested), query)

    def test_nested_in_null(self):
        class Nested(slothql.Object):
            nested = slothql.Field(self.query_class(), resolver=lambda *_: None)

        query = 'query { nested { hello } }'
        assert {'data': {'nested': None}} == slothql.gql(slothql.Schema(query=Nested), query)


def test_camelcase_schema_integration__queries():
    class FooBar(slothql.Object):
        foo_bar = slothql.Field(lambda: FooBar, resolver=lambda: {})
        some_weird_field = slothql.String(resolver=lambda: 'some weird field')

    class Query(slothql.Object):
        string_field = slothql.String(resolver=lambda: 'string field')
        foo_bar = slothql.Field(FooBar, resolver=lambda: {})

    schema = slothql.Schema(query=Query, auto_camelcase=True)
    assert {'data': {'stringField': 'string field', 'fooBar': {'someWeirdField': 'some weird field'}}} \
        == slothql.gql(schema, 'query { stringField fooBar { someWeirdField } }')

    # shouldn't modify the actual types
    assert {'string_field', 'foo_bar'} == Query()._meta.fields.keys()
    assert {'some_weird_field', 'foo_bar'} == FooBar()._meta.fields.keys()


def test_camelcase_schema_integration__introspection_query():
    class Query(slothql.Object):
        field = slothql.String()

    schema = slothql.Schema(query=Query, auto_camelcase=True)
    assert 'errors' not in slothql.gql(schema, graphql.introspection_query)

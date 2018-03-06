import pytest

from graphql import graphql

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
        assert 'world' == graphql(schema, query).data['hello']

    @pytest.mark.parametrize('call', (True, False))
    def test_complex_schema(self, call):
        class Nested(slothql.Object):
            nested = slothql.Field(self.query_class() if call else self.query_class, lambda *_: {'world': 'not hello'})

        query = 'query { nested { hello } }'
        assert {'nested': {'hello': 'world'}} == graphql(slothql.Schema(query=Nested), query).data

    def test_nested_in_null(self):
        class Nested(slothql.Object):
            nested = slothql.Field(self.query_class(), resolver=lambda *_: None)

        query = 'query { nested { hello } }'
        assert {'nested': None} == graphql(slothql.Schema(query=Nested), query).data


def test_schema_camelcase_integration__queries():
    class FooBar(slothql.Object):
        some_weird_field = slothql.String(resolver=lambda: 'some weird field')

    class Query(slothql.Object):
        string_field = slothql.String(resolver=lambda: 'string field')
        foo_bar = slothql.Field(FooBar, resolver=lambda: {})

    schema = slothql.Schema(query=Query, auto_camelcase=True)
    assert {'data': {'stringField': 'string field', 'fooBar': {'someWeirdField': 'some weird field'}}} \
        == slothql.gql(schema, 'query { stringField fooBar { someWeirdField } }')

    # shouldn't modify the actual types
    assert {'string_field', 'foo_bar'} == Query()._type.fields.keys() == Query()._type._fields.keys()
    assert {'some_weird_field'} == FooBar()._type.fields.keys() == FooBar()._type._fields.keys()

import pytest

from graphql import graphql

import slothql


@pytest.mark.incremental
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

    @pytest.mark.parametrize("call", (
            True,
            False,
    ))
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

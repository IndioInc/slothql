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

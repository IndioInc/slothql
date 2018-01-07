import pytest

from graphql import graphql

import slothql


# @pytest.mark.incremental
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

    @pytest.mark.skip(reason='needs additional development')
    def test_exception_not_handled(self):
        def resolve(*_):
            raise KeyError

        class Query(slothql.Object):
            hello = slothql.String(resolver=resolve)
        with pytest.raises(Exception):
            print(graphql(slothql.Schema(query=Query), 'query { hello }').data)

    @pytest.mark.parametrize("call", (
            True,
            False,
    ))
    def test_complex_schema(self, call):
        def resolve_nested(*_):
            return {'world': 'not hello'}

        class Nested(slothql.Object):
            nested = slothql.Field(self.query_class() if call else self.query_class, resolver=resolve_nested)

        query = 'query { nested { hello } }'
        assert {'nested': {'hello': 'world'}} == graphql(slothql.Schema(query=Nested), query).data

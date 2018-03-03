import pytest

import slothql

pytestmark = pytest.mark.incremental


def test_field_source(type_mock, info_mock):
    class A(slothql.Object):
        foo = slothql.Field(type_mock(), source='bar')

    assert 'baz' == A.foo.resolve_field({'bar': 'baz'}, info_mock(field_name='foo'), {})


def test_integration():
    class A(slothql.Object):
        foo = slothql.String(source='bar')

    class Query(slothql.Object):
        a = slothql.Field(A, resolver=lambda: {'bar': 'baz'})

    assert {'data': {'a': {'foo': 'baz'}}} == slothql.gql(slothql.Schema(Query), query='query { a { foo } }')

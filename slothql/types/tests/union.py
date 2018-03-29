import pytest

import slothql


def test_union_type__empty_types():
    with pytest.raises(AssertionError) as exc_info:
        class Foo(slothql.Union):
            class Meta:
                union_types = ()
    assert '`Foo`.`union_types` has to be an iterable of Object, not ()' == str(exc_info.value)


def test_union_type__missing_type_resolvers():
    class A(slothql.Object):
        a = slothql.Integer()

    class B(slothql.Object):
        b = slothql.String()

    with pytest.raises(AssertionError) as exc_info:
        class Foo(slothql.Union):
            class Meta:
                union_types = (A, B)
    assert '`Foo` has to provide a `resolve_type` method or each subtype has to provide a `is_type_of` method' \
           == str(exc_info.value)


def test_union_type__abstract():
    class A(slothql.Object):
        a = slothql.Integer()

    class B(slothql.Object):
        b = slothql.String()

    class Foo(slothql.Union):
        class Meta:
            abstract = True
            union_types = ()


def test_union_type__is_type_of():
    class A(slothql.Object):
        a = slothql.Integer()

        @classmethod
        def is_type_of(cls, obj, info: slothql.ResolveInfo) -> bool:
            return 'a' in obj

    class B(slothql.Object):
        b = slothql.String()

        @classmethod
        def is_type_of(cls, obj, info: slothql.ResolveInfo) -> bool:
            return 'b' in obj

    class Foo(slothql.Union):
        class Meta:
            union_types = (A, B)

    class Query(slothql.Object):
        foo = slothql.Field(Foo, many=True, resolver=lambda: [{'a': 1}, {'b': '2'}])

    schema = slothql.Schema(query=Query)
    query = 'query { foo {  ... on A { a } ... on B { b } } }'
    assert {'data': {'foo': [{'a': 1}, {'b': '2'}]}} == slothql.gql(schema, query)


def test_union_type_missing_resolve_type():
    class A(slothql.Object):
        a = slothql.Integer()

    class B(slothql.Object):
        b = slothql.String()

    class Foo(slothql.Union):
        class Meta:
            union_types = (A, B)

        @classmethod
        def resolve_type(cls, obj, info):
            return A if 'a' in obj else B

    class Query(slothql.Object):
        foo = slothql.Field(Foo, many=True, resolver=lambda: [{'a': 1}, {'b': '2'}])

    schema = slothql.Schema(query=Query)
    query = 'query { foo {  ... on A { a } ... on B { b } } }'
    assert {'data': {'foo': [{'a': 1}, {'b': '2'}]}} == slothql.gql(schema, query)

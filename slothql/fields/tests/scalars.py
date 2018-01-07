import pytest
from unittest import mock

from graphql.type.definition import GraphQLType

from ..scalars import Field, Scalar, String


@pytest.mark.incremental
class TestScalar:
    def test_can_init(self):
        Scalar(of_type=GraphQLType())

    def test_default_serialize(self):
        obj = object()
        assert obj == Scalar.serialize(obj)

    def test_resolve(self):
        obj, resolver, info = object(), object(), object()
        with mock.patch.object(Field, 'resolve', return_value=obj) as super_resolve:
            with mock.patch.object(Scalar, 'serialize', return_value=obj) as serialize:
                assert obj == Scalar.resolve(resolver, obj, info)
        super_resolve.assert_called_once_with(resolver, obj, info)
        serialize.assert_called_once_with(obj)


@pytest.mark.incremental
class TestString:
    def test_can_init(self):
        String()

    @pytest.mark.parametrize("value, expected", [
        ('123', '123'),
        (234, '234'),
        ({}, '{}'),
        ({'a': [1]}, "{'a': [1]}"),
    ])
    def test_serialize(self, value, expected):
        assert expected == String.serialize(value)

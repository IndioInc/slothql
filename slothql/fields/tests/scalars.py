import pytest
from unittest import mock

from graphql.type.definition import GraphQLType

from ..scalars import Field, Scalar, JSONString, String, Integer, Bool, Float, ID


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


def test_can_init_bool():
    Bool()


def test_can_init_integer():
    Integer()


def test_can_init_float():
    Float()


def test_can_init_string():
    String()


def test_can_init_json_string():
    JSONString()


def test_can_init_json_id():
    ID()

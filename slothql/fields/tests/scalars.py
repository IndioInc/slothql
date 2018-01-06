import pytest
from unittest import mock

from graphql.type.definition import GraphQLType

from ..scalars import Field, ScalarField, StringField


@pytest.mark.incremental
class TestScalarField:
    def test_can_init(self):
        ScalarField(of_type=GraphQLType())

    def test_default_serialize(self):
        obj = object()
        assert obj == ScalarField.serialize(obj)

    def test_resolve(self):
        obj, resolver, info = object(), object(), object()
        with mock.patch.object(Field, 'resolve', return_value=obj) as super_resolve:
            with mock.patch.object(ScalarField, 'serialize', return_value=obj) as serialize:
                assert obj == ScalarField.resolve(resolver, obj, info)
        super_resolve.assert_called_once_with(resolver, obj, info)
        serialize.assert_called_once_with(obj)


@pytest.mark.incremental
class TestStringField:
    def test_string_field_init(self):
        StringField()

    @pytest.mark.parametrize("value, expected", [
        ('123', '123'),
        (234, '234'),
        ({}, '{}'),
        ({'a': [1]}, "{'a': [1]}"),
    ])
    def test_serialize(self, value, expected):
        assert expected == StringField.serialize(value)

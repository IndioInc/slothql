import pytest
from unittest import mock

from graphql.type.definition import GraphQLType

import slothql
from slothql.types.base import BaseType
from ..scalars import Field, SerializableMixin


@pytest.mark.incremental
class TestSerializableMixin:
    def test_can_init(self):
        SerializableMixin(of_type=BaseType(type_=GraphQLType()))

    def test_default_serialize(self):
        obj = object()
        assert obj == SerializableMixin.serialize(obj)

    def test_resolve(self, info_mock):
        obj, resolver, info = object(), object(), info_mock()
        with mock.patch.object(Field, 'resolve', return_value=obj) as super_resolve:
            with mock.patch.object(SerializableMixin, 'serialize', return_value=obj) as serialize:
                assert obj == SerializableMixin.resolve(resolver, obj, info)
        super_resolve.assert_called_once_with(resolver, obj, info)
        serialize.assert_called_once_with(obj)


@pytest.mark.parametrize('scalar_type', (
        slothql.Boolean,
        slothql.Integer,
        slothql.Float,
        slothql.String,
        slothql.JSONString,
        slothql.ID,
        slothql.DateTime,
        slothql.Date,
        slothql.Time,
))
def test_passing_kwargs(scalar_type):
    scalar_type()

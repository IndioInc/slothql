import pytest
from unittest import mock

from slothql import fields

from ..object_type import Object, ObjectOptions


def test_cannot_init():
    with pytest.raises(AssertionError, message='Abstract type ObjectType can not be created'):
        Object()


@pytest.mark.incremental
class TestObjectMeta:
    def test_class_has_meta(self):
        assert hasattr(Object, '_meta')

    def test_object_abstract(self):
        assert Object._meta.abstract is True

    def test_object_class(self):
        assert isinstance(Object._meta, ObjectOptions)


@pytest.mark.incremental
class TestObjectInheritance:
    def test_can_inherit(self):
        class Inherit(Object):
            pass

    def test_inherited_not_abstract(self):
        class Inherit(Object):
            pass
        assert not Inherit._meta.abstract

    def test_can_create_not_abstract(self):
        class Inherit(Object):
            pass
        assert Inherit().name == 'Inherit'

    def test_abstract_inherit(self):
        class Inherit(Object):
            class Meta:
                abstract = True
        assert Inherit._meta.abstract

    def test_can_not_init_abstract(self):
        class Inherit(Object):
            class Meta:
                abstract = True
        with pytest.raises(AssertionError, message='Abstract type Inherit can not be created'):
            Inherit()


@pytest.mark.incremental
class TestObjectFields:
    def test_meta_has_fields(self):
        assert isinstance(getattr(Object._meta, 'fields'), dict)
        assert not Object._meta.fields

    def test_can_add_fields(self):
        class Inherit(Object):
            field = fields.Field(mock.Mock(spec=Object))
        assert Inherit.field == Inherit._meta.fields.get('field')

    def test_attributes_are_not_fields(self):
        class Inherit(Object):
            field = 'attribute'
        assert 'field' not in Inherit._meta.fields

    def test_fields(self):
        class Inherit(Object):
            field = fields.Field(mock.Mock(spec=Object))
        assert Inherit._meta.fields == Inherit().fields


def test_merge_object_options_dicts():
    assert ObjectOptions.merge_attributes(
        {'fields': {'a': 1, 'a_b': 1}},
        {'fields': {'a_b': 2, 'b': 2, 'extra_b': 2}},
    ) == {'fields': {'a': 1, 'a_b': 2, 'b': 2, 'extra_b': 2}}


def test_field_inheritance():
    class Base(Object):
        base = fields.Field(mock.Mock(spec=Object))

    class A(Base):
        a = fields.Field(mock.Mock(spec=Object))

    assert {'base': Base.base, 'a': A.a} == A._meta.fields


def test_field_multi_inheritance():
    class BaseA(Object):
        base = fields.Field(mock.Mock(spec=Object))
        base_a = fields.Field(mock.Mock(spec=Object))

    class BaseB(Object):
        base = fields.Field(mock.Mock(spec=Object))
        base_b = fields.Field(mock.Mock(spec=Object))

    class A(BaseA, BaseB):
        a = fields.Field(mock.Mock(spec=Object))

    assert {'base': BaseA.base, 'base_a': BaseA.base_a, 'base_b': BaseB.base_b, 'a': A.a} == A._meta.fields

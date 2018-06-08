import pytest
from unittest import mock

import inspect

import slothql
from slothql.types import fields

from ..object import Object, ObjectOptions


def test_cannot_init():
    with pytest.raises(
        AssertionError, message="Abstract type ObjectType can not be created"
    ):
        Object()


@pytest.mark.incremental
class TestObjectMeta:
    def test_class_has_meta(self):
        assert hasattr(Object, "_meta")

    def test_object_abstract(self):
        assert Object._meta.abstract is True

    def test_object_class(self):
        assert isinstance(Object._meta, ObjectOptions)


def test_cannot_add_extra_meta_attributes():
    with pytest.raises(AttributeError) as exc_info:

        class Inherit(Object):
            class Meta:
                abstract = True
                foo = True

    assert 'Meta received an unexpected attribute "foo = True"' == str(exc_info.value)


@pytest.mark.incremental
class TestObjectInheritance:
    def test_can_inherit(self):
        class Inherit(Object):
            class Meta:
                abstract = True

    def test_inherited_not_abstract(self):
        class Inherit(Object):
            field = fields.Field(mock.Mock(spec=Object))

        assert not Inherit._meta.abstract

    def test_can_create_not_abstract(self, field_mock):
        class Inherit(Object):
            field = field_mock

        assert "Inherit" == Inherit._meta.name

    def test_abstract_inherit(self):
        class Inherit(Object):
            class Meta:
                abstract = True

        assert Inherit._meta.abstract

    def test_can_not_init_abstract(self):
        class Inherit(Object):
            class Meta:
                abstract = True

        with pytest.raises(
            AssertionError, message="Abstract type Inherit can not be created"
        ):
            Inherit()


@pytest.mark.incremental
class TestObjectFields:
    def test_meta_has_fields(self):
        assert isinstance(getattr(Object._meta, "fields"), dict)
        assert not Object._meta.fields

    def test_can_add_fields(self):
        class Inherit(Object):
            field = fields.Field(Object)

        assert Inherit.field == Inherit._meta.fields.get("field")

    def test_attributes_are_not_fields(self):
        class Inherit(Object):
            field = "attribute"

            class Meta:
                abstract = True

        assert "field" not in Inherit._meta.fields


def test_field_inheritance():
    class Base(Object):
        base = fields.Field(Object)

    class A(Base):
        a = fields.Field(Object)

    assert {"base": Base.base, "a": A.a} == A._meta.fields


def test_field_multi_inheritance():
    class BaseA(Object):
        base = fields.Field(Object)
        base_a = fields.Field(Object)

    class BaseB(Object):
        base = fields.Field(Object)
        base_b = fields.Field(Object)

    class A(BaseA, BaseB):
        a = fields.Field(mock.Mock(spec=Object))

    assert {
        "base": BaseA.base,
        "base_a": BaseA.base_a,
        "base_b": BaseB.base_b,
        "a": A.a,
    } == A._meta.fields


def test_no_fields():
    with pytest.raises(AssertionError) as exc_info:

        class NoFields(Object):
            pass

    assert (
        '"NoFields" has to provide some fields, or use "class Meta: abstract = True"'
        == str(exc_info.value)
    )


def test_no_fields_abstract():
    class NoFieldsAbstract(Object):
        class Meta:
            abstract = True


def test_resolver_lambda(info_mock):
    class Test(Object):
        field = slothql.String(resolver=lambda obj: obj)

    expected = object()
    assert expected == Test.field.resolver(expected, info_mock(field_name="field"))


def test_resolver_staticmethod(info_mock):
    class Test(Object):
        @staticmethod
        def get_field(obj):
            return obj

        field = slothql.String(resolver=get_field)

    expected = object()
    assert expected == Test.field.resolver(expected, info_mock(field_name="field"))


def test_resolver_classmethod(info_mock):
    class Test(Object):
        @classmethod
        def get_field(cls, obj):
            return obj

        field = slothql.String(resolver=get_field)

    expected = object()
    assert expected == Test.field.resolver(expected, info_mock(field_name="field"))


def test_resolver_method(info_mock):
    class Test(Object):
        def get_field(self, obj):
            return obj

        field = slothql.String(resolver=get_field)

    expected = object()
    assert expected == Test.field.resolver(expected, info_mock(field_name="field"))


def test_name_collision__fields():
    class Query(slothql.Object):
        fields = slothql.String(resolver=lambda: "foo")

    slothql.Schema(query=Query)


def test_name_collision__interfaces():
    class Query(slothql.Object):
        interfaces = slothql.String(resolver=lambda: "foo")

    slothql.Schema(query=Query)


def test_object_field_construction():
    class Foo(slothql.Object):
        string = slothql.String()
        float = slothql.Float()
        bool = slothql.Float()

    filter_class = Foo.filter_class
    assert inspect.isclass(filter_class)
    assert {
        "string": slothql.String(),
        "float": slothql.Float(),
        "bool": slothql.Boolean(),
    } == filter_class._meta.fields

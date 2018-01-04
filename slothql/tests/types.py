import pytest

from ..types import ObjectType


def test_can_not_init():
    with pytest.raises(AssertionError, message='Abstract type ObjectType can not be initialized'):
        ObjectType()


def test_can_not_init_abstract():
    class Inherit(ObjectType):
        class Meta:
            abstract = True
    with pytest.raises(AssertionError, message='Abstract type Inherit can not be initialized'):
        Inherit()


@pytest.mark.skip(reason='not implemented yet')
def test_can_add_fields():
    pass


@pytest.mark.skip(reason='not implemented yet')
def test_attributes_are_not_fields():
    pass


def test_class_has_meta():
    assert hasattr(ObjectType, '_meta')


def test_object_type_abstract():
    assert ObjectType._meta.abstract is True


def assert_inherited_not_abstract():
    class Inherit(ObjectType):
        pass

    assert not Inherit._meta.abstract

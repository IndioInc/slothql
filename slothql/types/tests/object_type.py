import pytest

from ..object_type import ObjectType


@pytest.mark.incremental
class TestObjectType:
    def test_class_has_meta(self):
        assert hasattr(ObjectType, '_meta')

    def test_object_type_abstract(self):
        assert ObjectType._meta.abstract is True

    def test_cannot_create_abstract(self):
        with pytest.raises(AssertionError, message='Abstract type ObjectType can not be created'):
            ObjectType()


@pytest.mark.incremental
class TestObjectTypeInheritance:
    def test_can_inherit(self):
        class Inherit(ObjectType):
            pass

    def test_inherited_not_abstract(self):
        class Inherit(ObjectType):
            pass
        assert not Inherit._meta.abstract

    def test_can_create_not_abstract(self):
        class Inherit(ObjectType):
            pass
        Inherit()

    def test_abstract_inherit(self):
        class Inherit(ObjectType):
            class Meta:
                abstract = True
        assert Inherit._meta.abstract

    def test_can_not_init_abstract(self):
        class Inherit(ObjectType):
            class Meta:
                abstract = True
        with pytest.raises(AssertionError, message='Abstract type Inherit can not be created'):
            Inherit()


@pytest.mark.skip(reason='not implemented yet')
def test_can_add_fields():
    pass


@pytest.mark.skip(reason='not implemented yet')
def test_attributes_are_not_fields():
    pass

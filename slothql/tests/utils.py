from .. import utils


class TestMagicName:
    @staticmethod
    def test_magic_method():
        assert utils.is_magic_name('__foo__')

    @staticmethod
    def test_startswith_dunder():
        assert not utils.is_magic_name('__bar')

    @staticmethod
    def test_endswith_dunder():
        assert not utils.is_magic_name('baz__')

    @staticmethod
    def test_no_dunder():
        assert not utils.is_magic_name('papa')


def test_merge_object_dicts():
    class A:
        field_a = 'a'
        field_a_b = 'a'

    class B(A):
        field_a_b = 'b'
        field_b = 'b'

    assert utils.get_object_attributes(B) == {'field_a': 'a', 'field_a_b': 'b', 'field_b': 'b'}

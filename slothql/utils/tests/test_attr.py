from ..attr import is_magic_name, get_attrs, get_attr_fields


def test_magic_name__magic_method():
    assert is_magic_name("__foo__")


def test_magic_name__startswith_dunder():
    assert not is_magic_name("__bar")


def test_magic_name__endswith_dunder():
    assert not is_magic_name("baz__")


def test_magic_name__no_dunder():
    assert not is_magic_name("papa")


class TestGetAttrs:
    @classmethod
    def setup_class(cls):
        class A:
            field_a = "a"
            field_a_b = "a"

            def method(self):
                pass

            @property
            def prop(self):
                return

        class B(A):
            field_a_b = "b"
            field_b = "b"

        cls.A, cls.B = A, B

    def test_get_attrs(self):
        assert get_attrs(self.B) == {
            "field_a": "a",
            "field_a_b": "b",
            "field_b": "b",
            "method": self.A.method,
            "prop": self.A.prop,
        }

    def test_get_attr_fields(self):
        return get_attr_fields(self.B) == {
            "field_a": "a",
            "field_a_b": "b",
            "field_b": "b",
        }

import pytest

from ..case import snake_to_camelcase


@pytest.mark.parametrize('value, expected', (
        ('', ''), ('_', '_'), ('__', '__'),
        ('fooBar', 'fooBar'),
        ('FooBar', 'FooBar'),
        ('foo_bar_baz', 'fooBarBaz'),
        ('foo__bar__baz', 'foo_Bar_Baz'),
        ('_foo_bar_baz', '_fooBarBaz'),
        ('__foo_bar_baz', '__fooBarBaz'),
        ('foo_bar_baz_', 'fooBarBaz_'),
        ('foo_bar_baz__', 'fooBarBaz__'),
        ('_foo_bar_baz_', '_fooBarBaz_'),
        ('__foo_bar_baz__', '__fooBarBaz__'),
))
def test_to_camelcase(value, expected):
    assert expected == snake_to_camelcase(value)

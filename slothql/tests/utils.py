from .. import utils


def test_magic_method():
    assert utils.is_magic_name('__foo__')


def test_startswith_dunder():
    assert not utils.is_magic_name('__bar')


def test_endswith_dunder():
    assert not utils.is_magic_name('baz__')


def test_no_dunder():
    assert not utils.is_magic_name('papa')

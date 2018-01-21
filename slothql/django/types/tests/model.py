from ..model import Model

import pytest


def test_is_abstract():
    assert Model._meta.abstract


def test_model__missing_meta():
    with pytest.raises(AssertionError) as exc_info:
        class Example(Model):
            pass
    assert f'class Example is missing "Meta" class' == str(exc_info.value)

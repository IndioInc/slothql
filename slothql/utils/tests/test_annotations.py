import typing

import pytest

from .. import annotations


class Foo:
    pass


@pytest.mark.parametrize(
    "value, annotation, valid",
    (
        (Foo(), Foo, True),
        (Foo(), Foo, True),
        (Foo, Foo, False),
        (object(), Foo, False),
        (object(), typing.Any, True),
        (None, typing.Any, True),
        (12, int, True),
        (12, bool, False),
        (True, bool, True),
        (12, str, False),
        ("12", str, True),
        (None, type(None), True),
        (1, type(None), False),
        ("12", typing.Union[int, str], True),
        (12, typing.Union[int, str], True),
        (None, typing.Union[int, str], False),
        (12, typing.Optional[int], True),
        (bool, typing.Optional[int], False),
        (None, typing.Optional[int], True),
        ([], list, True),
        ([], typing.List, True),
        ([], typing.List[int], True),
        ([1, 2], typing.List[int], True),
        ([1, "str"], typing.List[int], False),
        (set(), set, True),
        ({}, set, False),
        (set(), typing.Set, True),
        ({1}, typing.Set[int], True),
        ({1, 2}, typing.Set[int], True),
        ({1, "str"}, typing.Set[int], False),
        ((), tuple, True),
        ((), typing.Tuple, True),
        ((), typing.Tuple[int], False),
        ((1, "str"), typing.Tuple, True),
        ((1,), typing.Tuple[int], True),
        (("1",), typing.Tuple[int], False),
        ((1,), typing.Tuple[int, str], False),
        ((1, "str"), typing.Tuple[int, str], True),
        (("str", 1), typing.Tuple[int, str], False),
        ({}, typing.Dict, True),
        ([], typing.Dict, False),
        ([], typing.Dict[str, int], False),
        ({"foo": 1}, typing.Dict[str, int], True),
        ({"foo": "1"}, typing.Dict[str, int], False),
        ({1: 1}, typing.Dict[str, int], False),
        (bool, typing.Type[bool], True),
        (bool, typing.Type[int], True),
        (str, typing.Type[str], True),
        ("", typing.Type[str], False),
    ),
)
def test_validate(value, annotation, valid: bool):
    assert valid is annotations.validate(value, annotation)

import pytest

from ..enum import Enum, EnumValue


def test_empty_enum():
    with pytest.raises(AssertionError) as excinfo:
        class Empty(Enum):
            pass
    assert '"Empty" is missing valid `Enum` values' == str(excinfo.value)


def test_enum_declaration():
    class Gender(Enum):
        MALE = EnumValue(value=1, description='lads')
        FEMALE = EnumValue(value=2.0, description='gals')
        UNKNOWN = EnumValue(value='3', description='nobody knows')

    assert {'MALE': (True, 'lads'), 'FEMALE': (2.0, 'gals'), 'UNKNOWN': ('3', 'nobody knows')} \
        == {v.name: (v.value, v.description) for v in Gender()._type.values}

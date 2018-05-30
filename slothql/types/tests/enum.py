import pytest

import slothql

from ..enum import Enum, EnumValue


def test_empty_enum():
    with pytest.raises(AssertionError) as exc_info:
        class Empty(Enum):
            pass
    assert '"Empty" is missing valid `Enum` values' == str(exc_info.value)


def test_enum_declaration():
    class Gender(Enum):
        MALE = EnumValue(value=1, description='lads')
        FEMALE = EnumValue(value=2.0, description='gals')
        UNKNOWN = EnumValue(value='3', description='nobody knows')

    assert {'MALE': (True, 'lads'), 'FEMALE': (2.0, 'gals'), 'UNKNOWN': ('3', 'nobody knows')} \
        == {name: (value.value, value.description) for name, value in Gender._meta.enum_values.items()}


@pytest.mark.parametrize('value, expected', (
        (1, 'MALE'),
        ('MALE', None),
        (2, 'FEMALE'),
        ('2', None),
))
def test_enum_integration(value, expected):
    class Gender(Enum):
        MALE = EnumValue(value=1, description='lads')
        FEMALE = EnumValue(value=2.0, description='gals')
        UNKNOWN = EnumValue(value='3', description='nobody knows')

    class Query(slothql.Object):
        gender = slothql.Field(Gender, resolver=lambda: value)

    schema = slothql.Schema(query=Query)

    assert {'data': {'gender': expected}} == slothql.gql(schema, 'query { gender }')

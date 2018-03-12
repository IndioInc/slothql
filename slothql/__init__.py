from .types.fields import Field, Integer, Float, String, Boolean, ID, JsonString, DateTime, Date, Time
from .types import BaseType, Object, Enum, EnumValue
from .schema import Schema
from .query import gql

__all__ = (
    # fields
    'Field',
    'Integer', 'Float', 'String', 'Boolean', 'ID',
    'JsonString',
    'DateTime', 'Date', 'Time',

    # types
    'BaseType',
    'Object',
    'Enum', 'EnumValue',

    'Schema',
    'gql',
)

try:
    from slothql import django
    __all__ += 'django',
except ImportError as e:
    if str(e) != "No module named 'django'":
        raise

from .selections import Selection, ResolveInfo
from .types.fields import Field, Integer, Float, String, Boolean, ID, JsonString, DateTime, Date, Time
from .types import BaseType, Object, Enum, EnumValue, Union
from .schema import Schema
from .operation import Operation, InvalidOperation
from .query import gql, ExecutionResult

__all__ = (
    # graphql
    'Selection',
    'ResolveInfo',

    # fields
    'Field',
    'Integer',
    'Float',
    'String',
    'Boolean',
    'ID',
    'JsonString',
    'DateTime',
    'Date',
    'Time',

    # types
    'BaseType',
    'Object',
    'Enum',
    'EnumValue',
    'Union',

    'Operation',
    'InvalidOperation',
    'Schema',
    'gql',
    'ExecutionResult',
)

try:
    from slothql import django
    __all__ += ('django',)
except ImportError as e:
    if str(e) != "No module named 'django'":
        raise

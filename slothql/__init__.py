from slothql.types.fields import *
from .types import *
from .schema import Schema
from .query import gql

try:
    from slothql import django
except ImportError as e:
    if str(e) != "No module named 'django'":
        raise

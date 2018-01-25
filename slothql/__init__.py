from .fields import *
from .types import *
from .schema import Schema
from .query import gql

try:
    from slothql import django
except ImportError:
    try:  # check if the ImportError was actually caused by django
        import django
        raise
    except ImportError:
        pass

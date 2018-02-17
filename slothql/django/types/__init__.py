from .model import Model
from . import scalars

try:
    from . import postgres
except ImportError as e:
    if str(e) != "No module named 'psycopg2'":
        raise

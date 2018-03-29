import json

from .scalars import StringType


class JsonStringType(StringType):
    JSON_TYPES = (int, float, bool, str, list, dict)

    @classmethod
    def replace_set_with_dict(cls, value):
        if isinstance(value, set):
            return cls.replace_set_with_dict(list(value))
        elif isinstance(value, list):
            return [cls.replace_set_with_dict(i) for i in value]
        elif isinstance(value, dict):
            return {k: cls.replace_set_with_dict(v) for k, v in value.items()}
        return value

    @classmethod
    def serialize(cls, value) -> str:
        try:
            return json.dumps(cls.replace_set_with_dict(value))
        except TypeError:
            raise TypeError(f'`{cls.__name__}.serialize` received invalid value {repr(value)}')

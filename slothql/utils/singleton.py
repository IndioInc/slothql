import typing as t


class Singleton(type):
    _instances: t.Dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def __copy__(self, instance):
        return instance

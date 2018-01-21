from typing import Union

import datetime

from .scalars import String


class DateTime(String):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.description = 'ISO-8601 formatted datetime string'

    @classmethod
    def serialize(cls, value: datetime.datetime):
        assert isinstance(value, datetime.datetime), f'Expected datetime.datetime instance, got {repr(value)}'
        return value.isoformat()


class Date(String):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.description = 'ISO-8601 formatted date string'

    @classmethod
    def serialize(cls, value: Union[datetime.datetime, datetime.date]):
        if isinstance(value, datetime.datetime):
            return value.date().isoformat()
        elif isinstance(value, datetime.date):
            return value.isoformat()
        raise AssertionError(f'Expected datetime.date or datetime.datetime instance, got {repr(value)}')


class Time(String):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.description = 'ISO-8601 formatted time string'

    @classmethod
    def serialize(cls, value: Union[datetime.datetime, datetime.time]):
        if isinstance(value, datetime.datetime):
            return value.time().isoformat()
        elif isinstance(value, datetime.time):
            return value.isoformat()
        raise AssertionError(f'Expected datetime.time or datetime.datetime instance, got {repr(value)}')

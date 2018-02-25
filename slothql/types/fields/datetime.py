from ..datetime import DateTimeType, DateType, TimeType
from .field import Field


class DateTime(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=DateTimeType, **kwargs)


class Date(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=DateType, **kwargs)


class Time(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=TimeType, **kwargs)

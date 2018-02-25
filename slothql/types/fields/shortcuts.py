from slothql.types.scalars import IntegerType, FloatType, StringType, BooleanType, IDType
from slothql.types.json import JsonStringType
from slothql.types.datetime import DateTimeType, DateType, TimeType
from slothql.types.enum import Enum
from .field import Field


class Integer(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=IntegerType, **kwargs)


class Float(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=FloatType, **kwargs)


class String(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=StringType, **kwargs)


class Boolean(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=BooleanType, **kwargs)


class ID(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=IDType, **kwargs)


class JsonString(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=JsonStringType, **kwargs)


class DateTime(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=DateTimeType, **kwargs)


class Date(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=DateType, **kwargs)


class Time(Field):
    def __init__(self, **kwargs):
        super().__init__(of_type=TimeType, **kwargs)

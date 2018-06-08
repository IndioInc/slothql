import datetime
import typing

from .scalars import StringType


class DateTimeType(StringType):
    class Meta:
        description = "ISO-8601 formatted datetime string"

    @classmethod
    def serialize(cls, value: datetime.datetime):
        assert isinstance(
            value, datetime.datetime
        ), f"Expected datetime.datetime instance, got {repr(value)}"
        return value.isoformat()


class DateType(StringType):
    class Meta:
        description = "ISO-8601 formatted date string"

    @classmethod
    def serialize(cls, value: typing.Union[datetime.datetime, datetime.date]):
        if isinstance(value, datetime.datetime):
            return value.date().isoformat()
        elif isinstance(value, datetime.date):
            return value.isoformat()
        raise AssertionError(
            f"Expected datetime.date or datetime.datetime instance, got {repr(value)}"
        )


class TimeType(StringType):
    class Meta:
        description = "ISO-8601 formatted time string"

    @classmethod
    def serialize(cls, value: typing.Union[datetime.datetime, datetime.time]):
        if isinstance(value, datetime.datetime):
            return value.time().isoformat()
        elif isinstance(value, datetime.time):
            return value.isoformat()
        raise AssertionError(
            f"Expected datetime.time or datetime.datetime instance, got {repr(value)}"
        )

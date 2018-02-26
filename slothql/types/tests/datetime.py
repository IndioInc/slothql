import pytest

import datetime

from ..datetime import DateTimeType, DateType, TimeType


@pytest.mark.parametrize('value, expected', (
        (datetime.datetime(2005, 4, 2, 21, 37, 9), '2005-04-02T21:37:09'),
        (datetime.datetime(2005, 4, 2), '2005-04-02T00:00:00'),
))
def test_datetime_serialize(value, expected):
    assert expected == DateTimeType.serialize(value)


@pytest.mark.parametrize('value', (
        datetime.date(2005, 4, 2),
        datetime.time(21, 37),
))
def test_datetime_serialize_type(value):
    with pytest.raises(AssertionError) as exc_info:
        DateTimeType.serialize(value)
    assert 'Expected datetime.datetime' in str(exc_info.value)


@pytest.mark.parametrize('value, expected', (
        (datetime.datetime(2005, 4, 2, 21, 37, 9), '2005-04-02'),
        (datetime.date(2005, 4, 2), '2005-04-02'),
))
def test_date_serialize(value, expected):
    assert expected == DateType.serialize(value)


@pytest.mark.parametrize('value', (
        datetime.time(21, 37),
))
def test_date_serialize_type(value):
    with pytest.raises(AssertionError) as exc_info:
        DateType.serialize(value)
    assert 'Expected datetime.date or datetime.datetime' in str(exc_info.value)


@pytest.mark.parametrize('value, expected', (
        (datetime.datetime(2005, 4, 2, 21, 37, 9), '21:37:09'),
        (datetime.time(21, 37, 9), '21:37:09'),
        (datetime.time(21, 37), '21:37:00'),
))
def test_time_serialize(value, expected):
    assert expected == TimeType.serialize(value)


@pytest.mark.parametrize('value', (
        datetime.date(2005, 4, 2),
))
def test_time_serialize_type(value):
    with pytest.raises(AssertionError) as exc_info:
        TimeType.serialize(value)
    assert 'Expected datetime.time or datetime.datetime' in str(exc_info.value)

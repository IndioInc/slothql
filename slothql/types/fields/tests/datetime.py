import pytest

import datetime

from ..datetime import DateTime, Date, Time


@pytest.mark.parametrize('value, expected', (
        (datetime.datetime(2005, 4, 2, 21, 37, 9), '2005-04-02T21:37:09'),
        (datetime.datetime(2005, 4, 2), '2005-04-02T00:00:00'),
))
def test_datetime_serialize(value, expected):
    assert expected == DateTime.serialize(value)


@pytest.mark.parametrize('value', (
        datetime.date(2005, 4, 2),
        datetime.time(21, 37),
))
def test_datetime_serialize_type(value):
    with pytest.raises(AssertionError) as exc_info:
        DateTime.serialize(value)
    assert 'Expected datetime.datetime' in str(exc_info.value)


@pytest.mark.parametrize('value, expected', (
        (datetime.datetime(2005, 4, 2, 21, 37, 9), '2005-04-02'),
        (datetime.date(2005, 4, 2), '2005-04-02'),
))
def test_date_serialize(value, expected):
    assert expected == Date.serialize(value)


@pytest.mark.parametrize('value', (
        datetime.time(21, 37),
))
def test_datetime_serialize_type(value):
    with pytest.raises(AssertionError) as exc_info:
        Date.serialize(value)
    assert 'Expected datetime.date or datetime.datetime' in str(exc_info.value)


@pytest.mark.parametrize('value, expected', (
        (datetime.datetime(2005, 4, 2, 21, 37, 9), '21:37:09'),
        (datetime.time(21, 37, 9), '21:37:09'),
        (datetime.time(21, 37), '21:37:00'),
))
def test_time_serialize(value, expected):
    assert expected == Time.serialize(value)


@pytest.mark.parametrize('value', (
        datetime.date(2005, 4, 2),
))
def test_time_serialize_type(value):
    with pytest.raises(AssertionError) as exc_info:
        Time.serialize(value)
    assert 'Expected datetime.time or datetime.datetime' in str(exc_info.value)

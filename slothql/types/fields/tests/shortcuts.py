import pytest
import slothql


@pytest.mark.parametrize(
    "field",
    (
        slothql.Boolean,
        slothql.Integer,
        slothql.Float,
        slothql.String,
        slothql.JsonString,
        slothql.ID,
        slothql.DateTime,
        slothql.Date,
        slothql.Time,
    ),
)
def test_field_init(field):
    assert field()._type

import pytest

from django.db import models

from ..model import get_model_attrs, get_selectable_relations, get_relations


def test_get_model_attrs__regular_field():
    class ModelAttrsField(models.Model):
        field = models.TextField()

        class Meta:
            app_label = "slothql.tests"

    attrs = get_model_attrs(ModelAttrsField)
    del attrs["id"]  # noqa
    assert attrs.keys() == {"field"} and isinstance(
        attrs.get("field"), models.TextField
    )


@pytest.mark.skip(reason="not implemented yet")
def test_get_model_attrs__method_field():
    class ModelAttrsMethod(models.Model):
        def method_field(self):
            return f"method"

        class Meta:
            app_label = "slothql.tests"

    assert get_model_attrs(ModelAttrsMethod) == {
        "method_field": ModelAttrsMethod.method_field
    }


@pytest.mark.skip(reason="not implemented yet")
def test_get_model_attrs__property_field():
    class ModelAttrsProperty(models.Model):
        @property
        def property_field(self):
            return f"property"

        class Meta:
            app_label = "slothql.tests"

    assert get_model_attrs(ModelAttrsProperty) == {
        "property_field": ModelAttrsProperty.property_field
    }


class A(models.Model):
    b_foreign = models.ForeignKey("B", models.CASCADE, related_name="a_objs")
    b_one2one = models.OneToOneField("B", models.CASCADE)
    b_many2many = models.ManyToManyField("B")

    field = models.TextField()

    class Meta:
        app_label = "slothql"


class B(models.Model):
    a_foreign = models.ForeignKey(A, models.CASCADE)
    a_one2one = models.OneToOneField(A, models.CASCADE, related_name="b_obj")
    a_many2many = models.ManyToManyField(A, related_name="b_objs")

    field = models.TextField()

    class Meta:
        app_label = "slothql"


@pytest.mark.parametrize(
    "model, expected_fields",
    ((A, {"b_foreign": B, "b_one2one": B}), (B, {"a_foreign": A, "a_one2one": A})),
)
def test_get_forward_relations(model, expected_fields: dict):
    assert expected_fields == get_selectable_relations(model)


@pytest.mark.parametrize(
    "model, expected_fields",
    (
        (
            A,
            {
                # forward relations
                "b_foreign": B,
                "b_one2one": B,
                "b_many2many": B,
                # backward relations
                "b_set": B,
                "b_obj": B,
                "b_objs": B,
            },
        ),
        (
            B,
            {
                # forward relations
                "a_foreign": A,
                "a_one2one": A,
                "a_many2many": A,
                # backward relations
                "a_objs": A,
                "a_set": A,
                "a": A,
            },
        ),
    ),
)
def test_get_relations(model, expected_fields: dict):
    assert expected_fields == get_relations(model)

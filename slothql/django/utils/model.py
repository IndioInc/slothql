from typing import Type

from django.db.models import Model


def get_model_attrs(model: Type[Model]) -> dict:
    return {
        field.name: field for field in model._meta.get_fields()
    }

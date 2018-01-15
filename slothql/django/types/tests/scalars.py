from django.db import models

import slothql
import slothql.django

from ..registry import TypeRegistry


class TestCharField:
    def test_registered(self):
        assert isinstance(TypeRegistry().get(models.CharField()), slothql.String)


class TestTextField:
    def test_registered(self):
        assert isinstance(TypeRegistry().get(models.TextField()), slothql.String)

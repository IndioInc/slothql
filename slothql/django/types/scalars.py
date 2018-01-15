from django.db import models

import slothql

from .registry import TypeRegistry


TypeRegistry().register(models.CharField, slothql.String())
TypeRegistry().register(models.TextField, slothql.String())

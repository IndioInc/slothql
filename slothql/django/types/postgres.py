from django.contrib.postgres import fields

import slothql

from .registry import TypeRegistry

TypeRegistry().register(fields.JSONField, slothql.JSONString())

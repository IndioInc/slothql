from django.db import models

import slothql

from .registry import TypeRegistry

TypeRegistry().register(models.AutoField, slothql.Integer())
TypeRegistry().register(models.BigAutoField, slothql.Integer())

TypeRegistry().register(models.CharField, slothql.String())
TypeRegistry().register(models.TextField, slothql.String())
TypeRegistry().register(models.EmailField, slothql.String())

TypeRegistry().register(models.IntegerField, slothql.Integer())
TypeRegistry().register(models.BigIntegerField, slothql.Integer())
TypeRegistry().register(models.PositiveIntegerField, slothql.Integer())
TypeRegistry().register(models.SmallIntegerField, slothql.Integer())
TypeRegistry().register(models.PositiveSmallIntegerField, slothql.Integer())

TypeRegistry().register(models.BooleanField, slothql.Boolean())
TypeRegistry().register(models.NullBooleanField, slothql.Boolean())

TypeRegistry().register(models.FloatField, slothql.Float())
TypeRegistry().register(models.DecimalField, slothql.Float())

TypeRegistry().register(models.DateTimeField, slothql.DateTime())
TypeRegistry().register(models.DateField, slothql.Date())
TypeRegistry().register(models.TimeField, slothql.Time())

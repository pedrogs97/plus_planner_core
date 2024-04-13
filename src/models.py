"""Provides the base model for all models in the application."""

from tortoise.models import Model
from tortoise import fields


class TesteModel(Model):
    """Base model for all models in the application."""

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=255)

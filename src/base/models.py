"""Provides the base model for all models in the application."""

from tortoise.models import Model
from tortoise import fields


class BaseModel(Model):
    """Base model for all models in the application."""

    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True

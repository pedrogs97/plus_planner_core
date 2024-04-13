"""This module contains the models of the clinic_office app."""

import datetime
from tortoise import fields
from src.base.models import BaseModel

# from src.base.enums import GenderEnum


class PacientModel(BaseModel):
    """Model to represent a pacient."""

    full_name = fields.CharField(max_length=255)
    taxpayer_id = fields.CharField(max_length=12)
    birth_date = fields.DateField(null=True)
    # gender = fields.CharEnumField(
    #     enum_type=GenderEnum, max_length=1, default=GenderEnum.O
    # )
    phone = fields.CharField(max_length=20, null=True)

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        """Calculate the age of the pacient."""
        return (datetime.date.today() - self.birth_date).days // 365

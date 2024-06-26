"""Schemas for the clinic_office module"""

from datetime import date
from typing import Optional

from plus_db_agent.enums import GenderEnum
from plus_db_agent.schemas import BaseSchema
from pydantic import Field


class NewPatientSchema(BaseSchema):
    """Schema for creating a new patient"""

    full_name: str = Field(alias="fullName")
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    birth_date: Optional[date] = Field(alias="birthDate", default=None)
    gender: Optional[GenderEnum] = GenderEnum.O
    phone: Optional[str] = None


class PatientSerializerSchema(BaseSchema):
    """Schema for a patient"""

    full_name: str = Field(alias="fullName")
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    birth_date: Optional[date] = Field(alias="birthDate", default=None)
    gender: GenderEnum
    phone: Optional[str] = None


class UpdatePatientSchema(BaseSchema):
    """Schema for updating a patient"""

    full_name: Optional[str] = Field(alias="fullName", default=None)
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    birth_date: Optional[date] = Field(alias="birthDate", default=None)
    gender: Optional[GenderEnum] = GenderEnum.O
    phone: Optional[str] = None

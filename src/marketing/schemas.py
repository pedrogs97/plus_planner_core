"""Schemas for the marketing module"""

from plus_db_agent.enums import GenderEnum
from plus_db_agent.schemas import BaseSchema
from pydantic import Field, field_validator

from src.config import ID_NOT_FOUND
from src.manager.repository import ClinicRepository
from src.marketing.repository import ProspectionStageRepository


class ProspectionStageSerializerSchema(BaseSchema):
    """ProspectionStage serializer schema"""

    id: int
    name: str
    color: str


class NewUpdateProspectionStageSchema(BaseSchema):
    """New and Update prospection stage schema"""

    name: str
    color: str


class ProspectionSerializerSchema(BaseSchema):
    """Prospection serializer schema"""

    id: int
    full_name: str = Field(serialization_alias="fullName")
    email: str
    phone: str
    gender: GenderEnum
    observation: str
    stage: ProspectionStageSerializerSchema


class NewUpdateProspectionSchema(BaseSchema):
    """New and Update prospection schema"""

    full_name: str = Field(alias="fullName")
    email: str
    phone: str
    gender: GenderEnum
    observation: str
    stage: int
    clinic: int

    @field_validator("stage")
    @classmethod
    async def validate_stage(cls, value):
        """Validate stage field"""
        stage = await ProspectionStageRepository().get_by_id(value)

        if not stage or value < 1:
            raise ValueError(f"{ID_NOT_FOUND} do estágio")

        return value

    @field_validator("clinic")
    @classmethod
    async def validate_clinic(cls, value):
        """Validate clinic field"""
        clinic = await ClinicRepository().get_by_id(value)

        if not clinic or value < 1:
            raise ValueError(f"{ID_NOT_FOUND} da clínica")

        return value

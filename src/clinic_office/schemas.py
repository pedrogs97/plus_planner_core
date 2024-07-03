"""Schemas for the clinic_office module"""

from datetime import date
from typing import List, Optional

from plus_db_agent.enums import GenderEnum
from plus_db_agent.schemas import BaseSchema
from pydantic import Field


class SpecialtySerializerSchema(BaseSchema):
    """Specialty serializer schema"""

    id: int
    name: str
    description: str


class NewUpdateSpecialtySchema(BaseSchema):
    """New and Update specialty schema"""

    name: str
    description: Optional[str]


class TreatmentSerializerSchema(BaseSchema):
    """Treatment serializer schema"""

    id: int
    name: str
    description: str
    number: str
    cost: float
    value: float
    observation: Optional[str] = ""


class PatientSerializerSchema(BaseSchema):
    """Schema for a patient"""

    full_name: str = Field(alias="fullName")
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    birth_date: Optional[date] = Field(alias="birthDate", default=None)
    gender: GenderEnum
    phone: Optional[str] = None


class NewPatientSchema(BaseSchema):
    """Schema for creating a new patient"""

    full_name: str = Field(alias="fullName")
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    birth_date: Optional[date] = Field(alias="birthDate", default=None)
    gender: Optional[GenderEnum] = GenderEnum.O
    phone: Optional[str] = None


class TreatmentPatientSerializerSchema(BaseSchema):
    """Schema for a treatment patient"""

    id: int
    treatment: TreatmentSerializerSchema
    patient: PatientSerializerSchema
    start_date: Optional[date] = Field(alias="startDate", default_factory=date.today)
    end_date: Optional[date] = Field(alias="endDate", default=None)
    observation: Optional[str] = ""


class NewUpdateTreatmentPatientSerializerSchema(BaseSchema):
    """Schema for a treatment patient"""

    id: int
    treatment: int
    patient: int
    start_date: Optional[date] = Field(alias="startDate", default_factory=date.today)
    end_date: Optional[date] = Field(alias="endDate", default=None)
    observation: Optional[str] = ""


class UpdatePatientSchema(BaseSchema):
    """Schema for updating a patient"""

    full_name: Optional[str] = Field(alias="fullName", default=None)
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    birth_date: Optional[date] = Field(alias="birthDate", default=None)
    gender: Optional[GenderEnum] = GenderEnum.O
    phone: Optional[str] = None
    treatments: Optional[List[NewUpdateTreatmentPatientSerializerSchema]] = []


class NewUpdateTreatmentSchema(BaseSchema):
    """New and Update treatment schema"""

    name: str
    description: str
    number: str
    cost: float
    value: float
    observation: Optional[str] = ""


class PlanSerializerSchema(BaseSchema):
    """Plan serializer schema"""

    id: int
    name: str
    description: str
    observation: str
    specialties: List[SpecialtySerializerSchema]
    treatments: List[TreatmentSerializerSchema]


class NewUpdatePlanSchema(BaseSchema):
    """New and Update plan schema"""

    name: str
    description: str
    observation: Optional[str] = ""
    specialties: Optional[List[int]] = []
    treatments: Optional[List[int]] = []


class DeskSerializerSchema(BaseSchema):
    """Desk serializer schema"""

    id: int
    number: int
    vacancy: bool
    capacity: int
    observation: str


class NewUpdateDeskSchema(BaseSchema):
    """New and Update desk schema"""

    number: int
    vacancy: Optional[bool] = True
    capacity: int
    observation: Optional[str] = ""


class QuestionSerializerSchema(BaseSchema):
    """Question serializer schema"""

    id: int
    question: str
    short_question: Optional[bool] = Field(alias="shortQuestion", default=False)


class NewUpdateQuestionSchema(BaseSchema):
    """New and Update question schema"""

    question: str
    short_question: Optional[bool] = Field(alias="shortQuestion", default=False)


class AnamnesisSerializerSchema(BaseSchema):
    """Anamnesis serializer schema"""

    id: int
    questions: List[QuestionSerializerSchema]
    name: str
    number: str
    description: str
    observation: str


class NewUpdateAnamnesisSchema(BaseSchema):
    """New and Update anamnesis schema"""

    questions: Optional[List[int]] = []
    name: str
    number: str
    description: str
    observation: Optional[str] = ""

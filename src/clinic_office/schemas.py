"""Schemas for the clinic_office module"""

from datetime import date
from typing import List, Optional

from plus_db_agent.enums import GenderEnum
from plus_db_agent.schemas import BaseSchema
from pydantic import Field, field_validator

from src.clinic_office.controller import (
    PatientController,
    QuestionController,
    SpecialtyController,
    TreatmentController,
)


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


class UrgencySerializerSchema(BaseSchema):
    """Urgency serializer schema"""

    id: int
    name: str
    description: str
    observation: str
    date: date


class NewUpdateUrgencySchema(BaseSchema):
    """New and Update urgency schema"""

    name: str
    description: str
    observation: Optional[str] = ""
    date = Field(default_factory=date.today)
    patient: int

    @field_validator("patient")
    @classmethod
    async def check_patient(cls, patient: int):
        """Check if the patient exists"""
        if patient < 1:
            raise ValueError("ID do paciente inválido")

        patient = await PatientController().get_obj_or_none(patient)
        if not patient:
            raise ValueError("Paciente não encontrado")

        return patient


class DocumentSerializerSchema(BaseSchema):
    """Document serializer schema"""

    id: int
    file_name: str = Field(alias="fileName")
    file_path: str = Field(alias="filePath")
    obeservation: str


class NewUpdateDocumentSchema(BaseSchema):
    """New and Update document schema"""

    file_name: str = Field(alias="fileName")
    file_path: str = Field(alias="filePath")
    obeservation: Optional[str] = ""
    patient: int

    @field_validator("file_path")
    @classmethod
    def check_file_path(cls, file_path: str):
        """Check if the file path is valid"""
        if not file_path:
            raise ValueError("Caminho do arquivo inválido")

        return file_path

    @field_validator("patient")
    @classmethod
    async def check_patient(cls, patient: int):
        """Check if the patient exists"""
        if patient < 1:
            raise ValueError("ID do paciente inválido")

        patient = await PatientController().get_obj_or_none(patient)
        if not patient:
            raise ValueError("Paciente não encontrado")

        return patient


class PatientSerializerSchema(BaseSchema):
    """Schema for a patient"""

    full_name: str = Field(alias="fullName")
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    birth_date: Optional[date] = Field(alias="birthDate", default=None)
    gender: GenderEnum
    phone: Optional[str] = None
    urgencies: Optional[List[UrgencySerializerSchema]] = []
    documents: Optional[List[DocumentSerializerSchema]] = []


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

    @field_validator("treatment")
    @classmethod
    async def check_treatment(cls, treatment: int):
        """Check if the treatment exists"""
        if treatment < 1:
            raise ValueError("ID do tratamento inválido")

        treatment = await TreatmentController().get_obj_or_none(treatment)
        if not treatment:
            raise ValueError("Tratamento não encontrado")

        return treatment

    @field_validator("patient")
    @classmethod
    async def check_patient(cls, patient: int):
        """Check if the patient exists"""
        if patient < 1:
            raise ValueError("ID do paciente inválido")

        patient = await PatientController().get_obj_or_none(patient)
        if not patient:
            raise ValueError("Paciente não encontrado")

        return patient


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

    @field_validator("specialties")
    @classmethod
    async def check_specialties(cls, specialties: List[int]):
        """Check if the specialties exists"""
        for specialty in specialties:
            if specialty < 1:
                raise ValueError("ID da especialidade inválido")

            specialty_db = await SpecialtyController().get_obj_or_none(specialty)
            if not specialty_db:
                raise ValueError("Especialidade não encontrada")

        return specialties

    @field_validator("treatments")
    @classmethod
    async def check_treatments(cls, treatments: List[int]):
        """Check if the treatments exists"""
        for treatment in treatments:
            if treatment < 1:
                raise ValueError("ID do tratamento inválido")

            treatment_db = await TreatmentController().get_obj_or_none(treatment)
            if not treatment_db:
                raise ValueError("Tratamento não encontrado")

        return treatments


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

    @field_validator("questions")
    @classmethod
    async def check_questions(cls, questions: List[int]):
        """Check if the questions exists"""
        for question in questions:
            if question < 1:
                raise ValueError("ID da pergunta inválido")

            question_db = await QuestionController().get_obj_or_none(question)
            if not question_db:
                raise ValueError("Pergunta não encontrada")

        return questions

"""Clinic office controller"""

from plus_db_agent.controller import GenericController
from plus_db_agent.models import (
    AnamnesisModel,
    DeskModel,
    PatientModel,
    PlanModel,
    QuestionModel,
    SpecialtyModel,
    TreatmentModel,
)

from src.clinic_office.repository import (
    AnamnesisRepository,
    DeskRepository,
    PatientRepository,
    PlanRepository,
    QuestionRepository,
    SpecialtyRepository,
    TreatmentRepository,
)
from src.clinic_office.schemas import (
    AnamnesisSerializerSchema,
    DeskSerializerSchema,
    PatientSerializerSchema,
    PlanSerializerSchema,
    QuestionSerializerSchema,
    SpecialtySerializerSchema,
    TreatmentSerializerSchema,
)


class PatientController(GenericController):
    """Patient controller class"""

    def __init__(self) -> None:
        self.model = PatientModel
        self.serializer = PatientSerializerSchema
        self.repository = PatientRepository()


class SpecialtyController(GenericController):
    """Specialty controller class"""

    def __init__(self) -> None:
        self.model = SpecialtyModel
        self.serializer = SpecialtySerializerSchema
        self.repository = SpecialtyRepository()


class TreatmentController(GenericController):
    """Treatment controller class"""

    def __init__(self) -> None:
        self.model = TreatmentModel
        self.serializer = TreatmentSerializerSchema
        self.repository = TreatmentRepository()


class PlanController(GenericController):
    """Plan controller class"""

    def __init__(self) -> None:
        self.model = PlanModel
        self.serializer = PlanSerializerSchema
        self.repository = PlanRepository()


class DeskController(GenericController):
    """Desk controller class"""

    def __init__(self) -> None:
        self.model = DeskModel
        self.serializer = DeskSerializerSchema
        self.repository = DeskRepository()


class AnamnesisController(GenericController):
    """Anamnesis controller class"""

    def __init__(self) -> None:
        self.model = AnamnesisModel
        self.serializer = AnamnesisSerializerSchema
        self.repository = AnamnesisRepository()


class QuestionController(GenericController):
    """Question controller class"""

    def __init__(self) -> None:
        self.model = QuestionModel
        self.serializer = QuestionSerializerSchema
        self.repository = QuestionRepository()

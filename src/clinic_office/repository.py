"""Clinic office repository"""

from plus_db_agent.models import (
    AnamnesisModel,
    DeskModel,
    PatientModel,
    PlanModel,
    QuestionModel,
    SpecialtyModel,
    TreatmentModel,
    UrgencyModel,
)
from plus_db_agent.repository import GenericRepository


class PatientRepository(GenericRepository):
    """Patient repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = PatientModel


class UrgencyRepository(GenericRepository):
    """Urgency repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = UrgencyModel


class SpecialtyRepository(GenericRepository):
    """Specialty repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = SpecialtyModel


class TreatmentRepository(GenericRepository):
    """Treatment repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = TreatmentModel


class PlanRepository(GenericRepository):
    """Plan repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = PlanModel


class DeskRepository(GenericRepository):
    """Desk repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = DeskModel


class AnamnesisRepository(GenericRepository):
    """Anamnesis repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = AnamnesisModel


class QuestionRepository(GenericRepository):
    """Question repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = QuestionModel

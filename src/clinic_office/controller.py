"""Clinic office controller"""

from plus_db_agent.controller import GenericController
from plus_db_agent.models import PatientModel

from src.clinic_office.repository import PatientRepository
from src.clinic_office.schemas import PatientSerializerSchema


class PatientController(GenericController):
    """Patient controller class"""

    def __init__(self) -> None:
        self.model = PatientModel
        self.serializer = PatientSerializerSchema
        self.repository = PatientRepository()

"""Clinic office service"""

from typing import List

from plus_db_agent.models import PatientModel
from plus_db_agent.schemas import BaseSchema
from plus_db_agent.service import GenericService

from src.clinic_office.controller import PatientController
from src.clinic_office.schemas import PatientSerializerSchema


class PatientService(GenericService):
    """Patient service class"""

    def __init__(self) -> None:
        self.controller = PatientController()
        self.serializer = PatientSerializerSchema
        self.model = PatientModel
        self.module_name = "clinic_office"

    async def list(self, **filters) -> List[BaseSchema]:
        super_list = await super().list(**filters)
        return [{"id": patient.id, "name": patient.name} for patient in super_list]

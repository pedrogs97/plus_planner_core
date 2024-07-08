"""This module contains the service classes for the marketing module"""

from typing import List

from plus_db_agent.models import ProspectionModel, ProspectionStageModel
from plus_db_agent.service import GenericService

from src.marketing.controller import ProspectionController, ProspectionStageController
from src.marketing.schemas import (
    ProspectionSerializerSchema,
    ProspectionStageSerializerSchema,
)


class ProspectionService(GenericService):
    """Prospection service class that will be inherited by all other services"""

    def __init__(self):
        self.controller = ProspectionController()
        self.serializer = ProspectionSerializerSchema
        self.model = ProspectionModel
        self.module_name = "prospection"


class ProspectionStageService(GenericService):
    """ProspectionStage service class that will be inherited by all other services"""

    def __init__(self):
        self.controller = ProspectionStageController()
        self.serializer = ProspectionStageSerializerSchema
        self.model = ProspectionStageModel
        self.module_name = "prospection_stage"

    async def list(self, **filters) -> List[dict]:
        super_list = await super().list(**filters)
        return [{"id": item["id"], "name": item["name"]} for item in super_list]

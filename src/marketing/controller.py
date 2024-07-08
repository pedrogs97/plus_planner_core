"""Marketing controller module"""

from plus_db_agent.controller import GenericController
from plus_db_agent.models import ProspectionModel, ProspectionStageModel

from src.marketing.repository import ProspectionRepository, ProspectionStageRepository
from src.marketing.schemas import (
    ProspectionSerializerSchema,
    ProspectionStageSerializerSchema,
)


class ProspectionController(GenericController):
    """Prospection controller class that will be inherited by all other controllers"""

    def __init__(self):
        self.model = ProspectionModel
        self.serializer = ProspectionSerializerSchema
        self.repository = ProspectionRepository()


class ProspectionStageController(GenericController):
    """ProspectionStage controller class that will be inherited by all other controllers"""

    def __init__(self):
        self.model = ProspectionStageModel
        self.serializer = ProspectionStageSerializerSchema
        self.repository = ProspectionStageRepository()

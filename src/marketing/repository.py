"""Marketing office repository"""

from plus_db_agent.models import ProspectionModel, ProspectionStageModel
from plus_db_agent.repository import GenericRepository


class ProspectionRepository(GenericRepository):
    """Prospection repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = ProspectionModel


class ProspectionStageRepository(GenericRepository):
    """ProspectionStage repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = ProspectionStageModel

"""Marketing filters"""

from typing import Optional

from plus_db_agent.enums import GenderEnum
from plus_db_agent.filters import BaseFilter
from plus_db_agent.models import ProspectionModel, ProspectionStageModel


class ProspectionFilter(BaseFilter):
    """Prospection filters"""

    full_name__icontains: Optional[str] = None
    email__icontains: Optional[str] = None
    phone__icontains: Optional[str] = None
    gender: Optional[GenderEnum] = None
    gender__in: Optional[GenderEnum] = None
    birth_date__gte: Optional[str] = None
    birth_date__lte: Optional[str] = None
    clinic_id__in: Optional[str] = None
    stage_id__in: Optional[str] = None
    order_by: Optional[str] = None
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = ProspectionModel
        search_model_fields = ["full_name", "email"]


class ProspectionStageFilter(BaseFilter):
    """ProspectionStage filters"""

    name__icontains: Optional[str] = None
    name__in: Optional[str] = None
    order_by: Optional[str] = None
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = ProspectionStageModel
        search_model_fields = ["name"]

"""Clinic office filters"""

from typing import Optional

from plus_db_agent.enums import GenderEnum
from plus_db_agent.filters import BaseFilter
from plus_db_agent.models import PatientModel


class PatientFilter(BaseFilter):
    """Patient filters"""

    full_name__icontains: Optional[str] = None
    taxpayer_id__icontains: Optional[str] = None
    gender: Optional[GenderEnum] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = PatientModel
        search_model_fields = ["full_name", "taxpayer_id"]

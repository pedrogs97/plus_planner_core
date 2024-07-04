"""Clinic office filters"""

from typing import List, Optional

from plus_db_agent.enums import GenderEnum
from plus_db_agent.filters import BaseFilter
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


class PatientFilter(BaseFilter):
    """Patient filters"""

    full_name__icontains: Optional[str] = None
    taxpayer_id__icontains: Optional[str] = None
    gender: Optional[GenderEnum] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = PatientModel
        search_model_fields = ["full_name", "taxpayer_id"]


class UrgencyFilter(BaseFilter):
    """Urgency filters"""

    name__icontains: Optional[str] = None
    description__icontains: Optional[str] = None
    date__gte: Optional[str] = None
    date__lte: Optional[str] = None
    order_by: List[str] = []
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = UrgencyModel
        search_model_fields = ["name", "description"]


class SpecialtyFilter(BaseFilter):
    """Specialty filters"""

    name__icontains: Optional[str] = None
    order_by: List[str] = []
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = SpecialtyModel
        search_model_fields = ["name", "description"]


class TreatmentFilter(BaseFilter):
    """Treatment filters"""

    name__icontains: Optional[str] = None
    number__icontains: Optional[str] = None
    cost__gte: Optional[float] = None
    cost__lte: Optional[float] = None
    value__gte: Optional[float] = None
    value__lte: Optional[float] = None
    order_by: List[str] = []
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = TreatmentModel
        search_model_fields = ["name", "description", "number"]


class PlanFilter(BaseFilter):
    """Plan filters"""

    name__icontains: Optional[str] = None
    order_by: List[str] = []
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = PlanModel
        search_model_fields = ["name", "description"]


class DeskFilter(BaseFilter):
    """Desk filters"""

    number: Optional[int] = None
    vacancy: Optional[bool] = None
    order_by: List[str] = []
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = DeskModel
        search_model_fields = []


class QuestionFilter(BaseFilter):
    """Question filters"""

    question__icontains: Optional[str] = None
    short_question: Optional[bool] = None
    order_by: List[str] = []
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = QuestionModel
        search_model_fields = ["question"]


class AnamnesisFilter(BaseFilter):
    """Anamnesis filters"""

    name__icontains: Optional[str] = None
    number__icontains: Optional[str] = None
    order_by: List[str] = []
    search: Optional[str] = None

    class Constants(BaseFilter.Constants):
        """Filter constants"""

        model = AnamnesisModel
        search_model_fields = ["name", "description", "number"]

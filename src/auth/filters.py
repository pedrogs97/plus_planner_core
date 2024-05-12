"""Auth filters"""

from typing import List, Optional

from src.auth.models import ProfileModel, UserModel
from src.base.filters import Filter


class ProfileFilter(Filter):
    """Profile filters"""

    name: Optional[str] = None
    name__icontains: Optional[str] = None

    class Constants(Filter.Constants):
        """Filter constants"""

        model = ProfileModel
        search_model_fields = ["name"]


class UserFilter(Filter):
    """User filters"""

    profile__name: Optional[str] = None
    full_name: Optional[str] = None
    username__icontains: Optional[str] = None
    email__icontains: Optional[str] = None
    taxpayer_id__icontains: Optional[str] = None
    is_active: Optional[bool] = None
    order_by: List[str] = []
    search: Optional[str] = None

    class Constants(Filter.Constants):
        """Filter constants"""

        model = UserModel
        search_model_fields = ["username", "email", "profile__name", "employee"]

"""Project backends."""
import logging
from typing import Annotated, List, Union

import jwt
from fastapi import Depends

from src.auth.models import PermissionModel, UserModel
from src.auth.schemas import PermissionSerializerSchema
from src.auth.service import UserService
from src.config import ALGORITHM, SECRET_KEY

logger = logging.getLogger(__name__)

user_service = UserService()


class PermissionChecker:
    """Dependence class for check permissions"""

    def __init__(
        self,
        required_permissions: Union[
            PermissionSerializerSchema, List[PermissionSerializerSchema]
        ],
    ) -> None:
        self.required_permissions = required_permissions

    def check_perm(
        self, perm_to_check: PermissionSerializerSchema, user_perm: PermissionModel
    ) -> bool:
        """Check if user has permission"""
        return (
            perm_to_check["module"] == user_perm.module
            and perm_to_check["model"] == user_perm.model
            and perm_to_check["action"] == user_perm.action
        )

    def has_permissions(self, user: UserModel) -> bool:
        """Check if user has permission"""

        if user.is_clinic_master:
            return True

        if isinstance(self.required_permissions, list):
            for perm in self.required_permissions:
                for perm_user in user.profile.permissions:
                    if self.check_perm(perm, perm_user):
                        return True
            return False

        for perm in user.profile.permissions:
            if self.check_perm(self.required_permissions, perm):
                return True

        return False

    def __call__(
        self,
        token: Annotated[str, Depends(user_service.oauth2_scheme)],
    ) -> Union[UserModel, None]:
        try:
            token_decoded = jwt.decode(str(token), SECRET_KEY, algorithms=ALGORITHM)
            if not user_service.token_is_valid(token_decoded):
                return None
            user = user_service.get_user_by_token(token_decoded)

            if not self.has_permissions(user):
                return None

            return user
        except jwt.ExpiredSignatureError:
            logger.warning("Invalid token")
            return None

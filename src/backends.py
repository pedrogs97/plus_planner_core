"""Project backends."""

import logging
from typing import Annotated, List, Union

import jwt
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from plus_db_agent.models import ClinicModel, PermissionModel, UserModel
from starlette.requests import Request

from src.auth.schemas import PermissionSerializerSchema
from src.auth.services_old import UserService
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
        me=False,
    ) -> None:
        self.required_permissions = required_permissions
        self.me = me

    def check_perm(
        self, perm_to_check: PermissionSerializerSchema, user_perm: PermissionModel
    ) -> bool:
        """Check if user has permission"""
        return (
            perm_to_check["module"] == user_perm.module
            and perm_to_check["model"] == user_perm.model
            and perm_to_check["action"] == user_perm.action
        )

    def has_permissions(
        self, user: UserModel, clinic: Union[ClinicModel, None]
    ) -> bool:
        """Check if user has permission"""

        if not user.is_active:
            return False

        if user.is_superuser or user.is_clinic_master or self.me:
            return True

        if clinic and user.clinic.id != clinic.id:
            return False

        if isinstance(self.required_permissions, list):
            return any(
                self.check_perm(perm, perm_user)
                for perm in self.required_permissions
                for perm_user in user.profile.permissions
            )

        return any(
            self.check_perm(self.required_permissions, perm)
            for perm in user.profile.permissions
        )

    async def __call__(
        self,
        request: Request,
        token: Annotated[str, Depends(user_service.oauth2_scheme)],
    ) -> Union[UserModel, None]:
        try:
            token_decoded = jwt.decode(str(token), SECRET_KEY, algorithms=ALGORITHM)
            if not user_service.token_is_valid(token_decoded):
                raise HTTPException(
                    detail={"message": "Não foi possível validar as credenciais"},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user = await user_service.get_user_by_token(token_decoded)

            if not user or not self.has_permissions(user, request.state.clinic):
                raise HTTPException(
                    detail={"message": "Usuário não autorizado"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            return user
        except jwt.ExpiredSignatureError as exc:
            logger.warning("Invalid token")
            raise HTTPException(
                detail={"message": "Não foi possível validar as credenciais"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc


class ClinicByHost:
    """Dependence class for get clinic by host"""

    async def __call__(
        self,
        request: Request,
    ) -> None:
        host = request.headers.get("host")
        if not host:
            request.state.clinic = None
            return
        if "127.0.0.1" in host:
            request.state.clinic = None
            return

        subdomain = host.split(".")[0]
        clinic = await ClinicModel.get_or_none(subdomain=subdomain)
        request.state.clinic = clinic

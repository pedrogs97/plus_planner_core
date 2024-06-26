"""Project backends."""

import logging
from typing import Annotated, List, Union

import jwt
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from plus_db_agent.models import ClinicModel, PermissionModel, UserModel
from starlette.requests import Request

from src.client import APIClient
from src.manager.schemas import PermissionSerializerSchema
from src.manager.service import UserService

logger = logging.getLogger(__name__)

user_service = UserService()


class PermissionChecker:
    """Dependence class for check permissions"""

    DEFAULT_MESSAGE = "Não foi possível validar as credenciais"

    def __init__(
        self,
        required_permissions: Union[
            PermissionSerializerSchema, List[PermissionSerializerSchema]
        ],
        me=False,
    ) -> None:
        self.required_permissions = required_permissions
        self.me = me
        self.api_client = APIClient()

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
            if not self.api_client.check_is_token_is_valid(token):
                raise HTTPException(
                    detail={"message": self.DEFAULT_MESSAGE},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user = await self.api_client.get_user_by_token(token)
            if user:
                await user.fetch_related("profile", "profile__permissions")
                if not self.has_permissions(user, request.state.clinic):
                    raise HTTPException(
                        detail={"message": "Usuário não autorizado"},
                        status_code=status.HTTP_403_FORBIDDEN,
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    detail={"message": "Usuário não encontrado"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            return user
        except jwt.ExpiredSignatureError as exc:
            logger.warning("Invalid token")
            raise HTTPException(
                detail={"message": self.DEFAULT_MESSAGE},
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

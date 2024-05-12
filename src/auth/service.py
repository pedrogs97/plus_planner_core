"""Auth service"""

import logging
import os
import random
import time
from datetime import datetime, timedelta
from typing import Union

import jwt
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import Page, Params, paginate
from tortoise.expressions import Q
from typing_extensions import Self

from src.auth.filters import UserFilter
from src.auth.models import ProfileModel, TokenModel, UserModel
from src.auth.schemas import (
    NewProfileSchema,
    NewUserSchema,
    PermissionSerializerSchema,
    ProfileSerializerSchema,
    ShortProfileSerializerSchema,
    UserSerializerSchema,
)
from src.config import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    bcrypt_context,
)
from src.log.services import LogService

logger = logging.Logger(__name__)


class UserService:
    """User service"""

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")

    _instance = None

    log_service = LogService()

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls._instance:
            cls._instance = super(UserService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __generate_random_password(self) -> str:
        """Generate random password"""
        return "".join(
            random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(12)
        )

    async def __get_new_token(self, user: UserModel) -> dict:
        """Generate new token"""
        await user.fetch_related("profile", "profile__permissions")
        profile = user.profile if user.profile else None
        if profile and profile.permissions:
            permissions = [
                f"{perm.module}_{perm.model}_{perm.action}"
                for perm in profile.permissions
            ]
        else:
            permissions = []

        access_expire_in = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        access_expire_timestamp = int(time.mktime(access_expire_in.timetuple()))

        encode = {
            "iat": datetime.now().timestamp(),
            "exp": access_expire_timestamp,
            "sub": user.id,
            "type": "access",
            "profile": profile.name if profile else "Super User",
            "email": user.email,
            "full_name": user.full_name,
            "permissions": permissions,
        }

        token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

        refresh_expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_expire_timestamp = time.mktime(refresh_expire.timetuple())

        refresh_encode = {
            "iat": datetime.now().timestamp(),
            "exp": refresh_expire_timestamp,
            "sub": user.id,
            "type": "refresh",
            "profile": profile.name if profile else "Super User",
            "email": user.email,
            "full_name": user.full_name,
            "permissions": permissions,
        }

        refresh_token = jwt.encode(refresh_encode, SECRET_KEY, algorithm=ALGORITHM)

        old_token = await TokenModel.get_or_none(user=user)
        if not old_token:
            await TokenModel.create(
                user=user,
                token=token,
                refresh_token=refresh_token,
                expires_at=access_expire_in,
                refresh_expires_at=refresh_expire,
            )
        else:
            old_token.token = token
            old_token.refresh_token = refresh_token
            old_token.expires_at = access_expire_in
            old_token.refresh_expires_at = (refresh_expire,)
            old_token.save()

        return {
            "access_token": token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_at": access_expire_timestamp,
        }

    async def create_superuser(self):
        """Create a test user"""
        profile_manager, _ = await ProfileModel.get_or_create(
            defaults={"name": "Manager"}
        )
        await UserModel.get_or_create(
            defaults={
                "full_name": os.getenv("DEFAULT_SUPERUSER_FULL_NAME", "Test User"),
                "password": self.hash_password(
                    os.getenv("DEFAULT_SUPERUSER_PASSWORD", "123456")
                ),
                "email": os.getenv("DEFAULT_SUPERUSER_EMAIL", "teste@email.com"),
                "username": os.getenv("DEFAULT_SUPERUSER_USERNAME", "test"),
                "is_superuser": True,
                "profile_id": profile_manager.id,
            }
        )

    async def get_or_404(self, user_id: int) -> UserModel:
        """Get user or raise 404"""
        user = await UserModel.get_or_none(id=user_id)
        await user.fetch_related("profile", "profile__permissions")
        if not user:
            raise HTTPException(
                detail={"field": "userId", "message": "Usuário não encontrado"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return user

    def serialize_user(self, user: UserModel) -> UserSerializerSchema:
        """Serialize user"""
        profile = ShortProfileSerializerSchema(**user.profile.__dict__)
        return UserSerializerSchema(**user.__dict__, profile=profile)

    def hash_password(self, password: str) -> str:
        """Hash password"""
        return bcrypt_context.hash(password)

    def password_is_correct(self, password: str, hashed_password: str) -> bool:
        """Verify if password is correct"""
        return bcrypt_context.verify(password, hashed_password)

    async def login(self, email_or_username: str, password: str) -> Union[dict, None]:
        """Try login a user"""
        user = await UserModel.filter(
            Q(email=email_or_username) | Q(username=email_or_username)
        ).first()

        if not user or not self.password_is_correct(password, user.password):
            return None

        if not user.profile and not user.is_superuser:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user.last_login_in = datetime.now()

        return await self.__get_new_token(user)

    def token_is_valid(self, token: Union[TokenModel, dict]) -> bool:
        """Verifies token validity"""
        if token and isinstance(token, TokenModel):
            return token.expires_at > datetime.now()

        if isinstance(token, dict) and token and "exp" in token:
            return (
                token["exp"] > datetime.now().timestamp() and token["type"] == "access"
            )
        return False

    async def get_user_by_token(
        self, token: Union[str, dict]
    ) -> Union[UserModel, None]:
        """Return a user by token"""
        try:
            token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        except (jwt.ExpiredSignatureError, jwt.PyJWTError):
            if isinstance(token, dict):
                token_decoded = token
            else:
                return None
        user = await UserModel.get_or_none(id=token_decoded["sub"])
        return user

    async def logout(self, token: str) -> None:
        """Logout a user"""
        try:
            token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user = await self.get_user_by_token(token_decoded)
            if not user:
                return
            old_token = await TokenModel.get(user=user)

            if not old_token:
                return
            old_token.delete()
        except jwt.PyJWTError:
            logger.warning("Failed logout")

    async def refresh_token(self, token: str) -> Union[dict, None]:
        """Refresh token"""
        try:
            token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user = await UserModel.get(id=token_decoded["sub"])
            if not user:
                return None

            return self.__get_new_token(user)
        except jwt.PyJWTError:
            return None

    async def request_reset_password(self, email: str) -> bool:
        """Request reset password"""
        user = await UserModel.get_or_none(email=email)
        if not user:
            return False
        # TODO: Implement email service
        return True

    async def reset_password(self, user: UserModel, new_password: str) -> bool:
        """Reset password"""
        user.password = self.hash_password(new_password)
        user.save()
        return True

    async def change_password(
        self, user: UserModel, old_password: str, new_password: str
    ) -> bool:
        """Change password"""
        if not self.password_is_correct(old_password, user.password):
            return False

        user.password = self.hash_password(new_password)
        user.save()
        return True

    async def create_user(
        self, user_data: NewUserSchema, authenticated_user: UserModel
    ) -> UserSerializerSchema:
        """Create a user"""
        new_random_password = self.__generate_random_password()
        # TODO: Implement email service to send password
        new_user = await UserModel.create(
            **user_data.model_dump(by_alias=False),
            password=self.hash_password(new_random_password),
        )
        self.log_service.set_log(
            module="auth",
            model="users",
            operation="Criação de usuário",
            identifier=new_user.id,
            user=authenticated_user,
        )
        return self.serialize_user(new_user)

    async def update_user(
        self, user_id: int, new_data: NewUserSchema, authenticated_user: UserModel
    ) -> UserSerializerSchema:
        """Update user"""
        user = await self.get_or_404(user_id)

        new_data_dict = new_data.model_dump(by_alias=False)
        profile_id = new_data_dict.pop("profile_id", None)
        profile = ProfileModel.get_or_none(id=profile_id)

        if not profile:
            raise HTTPException(
                detail={"field": "profile_id", "messsage": "Perfil não encontrado"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        is_clinic_master = new_data_dict.pop("is_clinic_master", None)

        if is_clinic_master is not None and authenticated_user.is_clinic_master:
            user.is_clinic_master = is_clinic_master

        user.profile = profile
        user.update_from_dict(new_data_dict)

        user.save()
        self.log_service.set_log(
            module="auth",
            model="users",
            operation="Atualização de usuário",
            identifier=user.id,
            user=authenticated_user,
        )
        return self.serialize_user(user)

    async def delete_user(self, user_id: int, autheticated_user: UserModel) -> bool:
        """Delete user"""
        user = await self.get_or_404(user_id)
        user.deleted = True
        user.save()
        self.log_service.set_log(
            module="auth",
            model="users",
            operation="Deleção de usuário",
            identifier=user.id,
            user=autheticated_user,
        )
        return True

    async def get_user(self, user_id: int) -> UserSerializerSchema:
        """Get user"""
        user = await self.get_or_404(user_id)
        return self.serialize_user(user)

    async def get_users(
        self,
        authenticated_user: UserModel,
        user_filters: UserFilter,
        page: int = 1,
        size: int = 50,
    ) -> Page[UserSerializerSchema]:
        """Get paginated users and apply filters"""
        user_list = user_filters.filter(
            UserModel.filter(id__not=authenticated_user.id).prefetch_related("profile")
        ).order_by("-created_at")

        params = Params(page=page, size=size)
        paginated = paginate(
            user_list,
            params=params,
            transformer=lambda user_list: [
                self.serialize_user(user).model_dump(by_alias=True)
                for user in user_list
            ],
        )
        return paginated


class ProfileService:
    """Profile Service"""

    _instance = None

    log_service = LogService()

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls._instance:
            cls._instance = super(ProfileService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    async def get_profile_or_404(self, profile_id: int) -> ProfileModel:
        """Get profile or raise 404"""
        profile = await ProfileModel.get_or_none(id=profile_id)
        if not profile:
            raise HTTPException(
                detail={"field": "profileId", "message": "Perfil não encontrado"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return profile

    def serializer_profile(self, profile: ProfileModel):
        """Serialize profile"""
        permissions_serializer = [
            PermissionSerializerSchema(**perm.__dict__) for perm in profile.permissions
        ]
        return ProfileSerializerSchema(
            **profile.__dict__, permissions=permissions_serializer
        )

    async def create_profile(
        self, new_profile: NewProfileSchema
    ) -> ProfileSerializerSchema:
        """Create a profile"""
        profile = await ProfileModel.create(**new_profile.model_dump(by_alias=False))
        self.log_service.set_log(
            module="auth",
            model="profiles",
            operation="Criação de perfil",
            identifier=profile.id,
            user=None,
        )
        return self.serializer_profile(profile)

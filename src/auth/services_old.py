"""Auth service"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Union

import jwt
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import Page, Params, paginate
from plus_db_agent.models import ClinicModel, ProfileModel, TokenModel, UserModel
from plus_db_agent.service import GenericService
from tortoise.expressions import Q

from src.auth.filters import ClinicFilter, ProfileFilter, UserFilter
from src.auth.repository import UserRepository
from src.auth.schemas import (
    ClinicSerializerSchema,
    NewUpdateClinicSchema,
    NewUpdateProfileSchema,
    NewUserSchema,
    ProfileSerializerSchema,
    UserListSerializerSchema,
    UserSerializerSchema,
)
from src.config import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    bcrypt_context,
)

logger = logging.Logger(__name__)


class UserService(GenericService):
    """User service"""

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")
    model = UserModel
    repository = UserRepository()

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
            "profile_id": profile.id if profile else "",
            "clinic": user.clinic.company_name if user.clinic else "",
            "clinic_id": user.clinic.id if user.clinic_id else "",
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
            "profile_id": profile.id if profile else "",
            "clinic": user.clinic.company_name if user.clinic else "",
            "clinic_id": user.clinic.id if user.clinic_id else "",
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

    def hash_password(self, password: str) -> str:
        """Hash password"""
        return bcrypt_context.hash(password)

    def password_is_correct(self, password: str, hashed_password: str) -> bool:
        """Verify if password is correct"""
        return bcrypt_context.verify(password, hashed_password)

    async def login(
        self, email_or_username: str, password: str, clinic: Union[ClinicModel, None]
    ) -> Union[dict, None]:
        """Try login a user"""
        user = await UserModel.filter(
            Q(email=email_or_username) | Q(username=email_or_username)
        ).first()

        if not user or not self.password_is_correct(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"detail": "Credenciais inválidas"},
            )

        if not clinic and not user.is_superuser:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if clinic and user.clinic != clinic:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

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

    async def logout(self, token: str, clinic: Union[ClinicModel, None]) -> None:
        """Logout a user"""
        try:
            token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user = await self.get_user_by_token(token_decoded)
            if not user and token_decoded["type"] != "access" and clinic != user.clinic:
                return
            old_token = await TokenModel.get(user=user)

            if not old_token:
                return
            old_token.delete()
        except jwt.PyJWTError:
            logger.warning("Failed logout")

    async def refresh_token(
        self, token: str, clinic: Union[ClinicModel, None]
    ) -> Union[dict, None]:
        """Refresh token"""
        try:
            token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user = await UserModel.get(id=token_decoded["sub"])
            if not user:
                return None

            if token_decoded["type"] != "refresh" and not self.token_is_valid(token):
                return None

            if clinic and user.clinic != clinic:
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
        return self.serializer_obj(new_user, UserSerializerSchema)

    async def get_users(
        self,
        authenticated_user: UserModel,
        user_filters: UserFilter,
        page: int = 1,
        size: int = 50,
    ) -> Page[UserSerializerSchema]:
        """Get paginated users and apply filters"""
        user_list = user_filters.filter(
            UserModel.filter(
                id__not=authenticated_user.id, clinic=authenticated_user.clinic
            ).prefetch_related("profile")
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


class ProfileService(GenericService):
    """Profile Service"""

    async def create_profile(
        self, new_profile: NewUpdateProfileSchema, authenticated_user: UserModel
    ) -> ProfileSerializerSchema:
        """Create a profile"""
        profile = await ProfileModel.create(
            **new_profile.model_dump(by_alias=False), clinic=authenticated_user.clinic
        )
        return self.serializer_profile(profile)

    async def get_profiles(
        self,
        authenticated_user: UserModel,
        profile_filters: ProfileFilter,
        page: int = 1,
        size: int = 50,
    ) -> Page[ProfileSerializerSchema]:
        """Get paginated profiles"""
        profile_list = profile_filters.filter(
            ProfileModel.filter(clinic=authenticated_user.clinic)
        ).order_by("-created_at")
        params = Params(page=page, size=size)
        paginated = paginate(
            profile_list,
            params=params,
            transformer=lambda profile_list: [
                self.serializer_profile(profile).model_dump(by_alias=True)
                for profile in profile_list
            ],
        )
        return paginated

    async def get_profiles_select(self, authenticated_user: UserModel):
        """Get profiles for select"""
        profile_list = await ProfileModel.filter(clinic=authenticated_user.clinic)
        return [{"id": profile.id, "name": profile.name} for profile in profile_list]


class ClinicService(GenericService):
    """Clinic Service"""

    async def get_clinic_or_404(self, clinic_id: int) -> ClinicModel:
        """Get clinic or raise 404"""
        clinic = await ClinicModel.get_or_none(id=clinic_id)
        if not clinic:
            raise HTTPException(
                detail={"field": "clinicId", "message": "Clinica não encontrada"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return clinic

    def serializer_clinic(self, clinic: ClinicModel) -> ClinicSerializerSchema:
        """Serialize clinic"""
        users = [UserListSerializerSchema(**user.__dict__) for user in clinic.users]
        return ClinicSerializerSchema(
            **clinic.__dict__,
            users=users,
            header_quarter=(
                clinic.head_quarter.company_name if clinic.head_quarter else ""
            ),
        )

    async def create_clinic(
        self, new_clinic: NewUpdateClinicSchema, authenticated_user: UserModel
    ) -> ClinicSerializerSchema:
        """Create a clinic"""
        clinic = await ClinicModel.create(
            **new_clinic.model_dump(by_alias=False),
            license=authenticated_user.clinic.license,
            subdomain=authenticated_user.clinic.subdomain,
        )
        return self.serializer_clinic(clinic)

    async def update_clinic(
        self,
        clinic_id: int,
        new_data: NewUpdateClinicSchema,
        authenticated_user: UserModel,
    ) -> ClinicSerializerSchema:
        """Update clinic"""
        clinic = await self.get_clinic_or_404(clinic_id)
        clinic.update_from_dict(new_data.model_dump(by_alias=False))
        clinic.save()
        return self.serializer_clinic(clinic)

    async def delete_clinic(
        self, clinic_id: int, authenticated_user: UserModel
    ) -> bool:
        """Delete clinic"""
        clinic = await self.get_clinic_or_404(clinic_id)
        clinic.delete()

        return True

    async def get_clinic(self, clinic_id: int) -> ClinicSerializerSchema:
        """Get clinic"""
        clinic = await self.get_clinic_or_404(clinic_id)
        return self.serializer_clinic(clinic)

    async def get_clinics(
        self,
        authenticated_user: UserModel,
        clinic_filters: ClinicFilter,
        page: int = 1,
        size: int = 50,
    ) -> Page[ClinicSerializerSchema]:
        """Get paginated clinics"""
        if authenticated_user.is_clinic_master:
            queryset = ClinicModel.filter(
                Q(head_quarter=authenticated_user.clinic)
                | Q(id=authenticated_user.clinic.id)
            )
        else:
            queryset = ClinicModel.filter(
                Q(head_quarter=authenticated_user.clinic.head_quarter)
                | Q(id=authenticated_user.clinic.head_quarter.id)
            )
        clinic_list = clinic_filters.filter(queryset).order_by("-created_at")
        params = Params(page=page, size=size)
        paginated = paginate(
            clinic_list,
            params=params,
            transformer=lambda clinic_list: [
                self.serializer_clinic(clinic).model_dump(by_alias=True)
                for clinic in clinic_list
            ],
        )
        return paginated

    async def get_clinics_select(self, authenticated_user: UserModel):
        """Get clinics for select"""
        if authenticated_user.is_clinic_master:
            queryset = ClinicModel.filter(
                Q(head_quarter=authenticated_user.clinic)
                | Q(id=authenticated_user.clinic.id)
            ).all()
        else:
            queryset = ClinicModel.filter(
                Q(head_quarter=authenticated_user.clinic.head_quarter)
                | Q(id=authenticated_user.clinic.head_quarter.id)
            ).all()
        return [{"id": clinic.id, "name": clinic.company_name} for clinic in queryset]

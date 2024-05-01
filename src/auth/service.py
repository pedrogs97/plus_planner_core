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
from tortoise.expressions import Q

from src.auth.models import TokenModel, UserModel
from src.auth.schemas import (
    NewUserSchema,
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

logger = logging.Logger(__name__)


class UserService:
    """User service"""

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")

    _instance = None

    def __new__(cls, *args, **kwargs):
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
        permissions = [
            f"{perm.module}_{perm.model}_{perm.action}"
            for perm in user.profile.permissions
        ]

        access_expire_in = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        access_expire_timestamp = int(time.mktime(access_expire_in.timetuple()))

        encode = {
            "iat": datetime.now().timestamp(),
            "exp": access_expire_timestamp,
            "sub": user.id,
            "type": "access",
            "profile": user.profile.name,
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
            "profile": user.profile.name,
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
            )
        else:
            old_token.token = token
            old_token.refresh_token = refresh_token
            old_token.expires_at = access_expire_in
            old_token.save()

        return {
            "access_token": token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_at": access_expire_timestamp,
        }

    def serialize_user(self, user: UserModel) -> UserSerializerSchema:
        """Serialize user"""
        profile = ShortProfileSerializerSchema(**user.profile.__dict__)
        return UserSerializerSchema(**user.__dict__, profile=profile)

    def has_password(self, password: str) -> str:
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

        if not user.profile:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user.last_login_in = datetime.now()

        return self.__get_new_token(user)

    def token_is_valid(self, token: Union[TokenModel, dict]) -> bool:
        """Verifies token validity"""
        if token and isinstance(token, TokenModel):
            return token.expires_at > datetime.now()

        if isinstance(token, dict) and token and "exp" in token:
            return (
                token["exp"] > datetime.now().timestamp() and token["type"] == "access"
            )
        return False

    async def get_user_by_token(self, token: str) -> Union[UserModel, None]:
        """Return a user by token"""
        try:
            token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user = await UserModel.get(id=token_decoded["sub"])
            return user
        except (jwt.ExpiredSignatureError, jwt.PyJWTError):
            return None

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
        user.password = self.has_password(new_password)
        user.save()
        return True

    async def change_password(
        self, user: UserModel, old_password: str, new_password: str
    ) -> bool:
        """Change password"""
        if not self.password_is_correct(old_password, user.password):
            return False

        user.password = self.has_password(new_password)
        user.save()
        return True

    async def create_user(self, user_data: NewUserSchema) -> UserSerializerSchema:
        """Create a user"""
        new_random_password = self.__generate_random_password()
        # TODO: Implement email service to send password
        new_user = await UserModel.create(
            **user_data.model_dump(by_alias=False),
            password=self.has_password(new_random_password),
        )
        return self.serialize_user(new_user)

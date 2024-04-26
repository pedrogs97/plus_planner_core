"""Auth service"""

import logging
import time
from datetime import datetime, timedelta
from typing import Union

import jwt
from fastapi import status
from fastapi.exceptions import HTTPException
from tortoise.expressions import Q

from src.auth.models import TokenModel, UserModel
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

    def password_is_correct(self, password: str, hashed_password: str) -> bool:
        """Verify if password is correct"""
        return bcrypt_context.verify(password, hashed_password)

    async def login(self, email_or_username: str, password: str) -> Union[dict, None]:
        """Try login a user"""
        user = await UserModel.filter(
            Q(email=email_or_username) | Q(username=email_or_username)
        ).first()

        if not user or self.password_is_correct(password, user.password):
            return None

        user.last_login_in = datetime.now()

        old_token = await TokenModel.get_or_none(user=user)

        if not user.profile:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        permissions = [
            f"{perm.module}_{perm.model}_{perm.action}"
            for perm in user.profile.permissions
        ]

        access_expire_in = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        access_expire_timestamp = int(time.mktime(access_expire_in.timetuple()))

        refresh_expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_expire_timestamp = time.mktime(refresh_expire.timetuple())
        if not self.token_is_valid(old_token):
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

            token_db = TokenModel(
                user=user,
                token=token,
                expires_at=access_expire_in,
                refresh_token=refresh_token,
                refresh_expires_at=refresh_expire,
            )

            if old_token:
                old_token.delete()

            token_db.save()

            return {
                "access_token": token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_at": access_expire_timestamp,
            }

        return {
            "id": user.id,
            "access_token": old_token.token,
            "refresh_token": old_token.refresh_token,
            "token_type": "Bearer",
            "expires_at": old_token.expires_at.timestamp(),
        }

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

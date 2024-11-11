"""Service for authentication"""

from datetime import datetime, timedelta
from typing import Union

import jwt
from fastapi.security import OAuth2PasswordBearer
from plus_db_agent.models import ClinicModel, TokenModel, UserModel
from tortoise.expressions import Q

from src.auth.logger import logger
from src.config import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    bcrypt_context,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")


def password_is_correct(password: str, hashed_password: str) -> bool:
    """Verify if password is correct"""
    return bcrypt_context.verify(password, hashed_password)


def hash_password(password: str) -> str:
    """Hash password"""
    return bcrypt_context.hash(password)


async def get_new_token(user: UserModel) -> dict:
    """Generate new token"""
    await user.fetch_related("profile", "profile__permissions", "clinic")
    profile = user.profile if user.profile else None
    if profile and profile.permissions:
        permissions = [
            f"{perm.module}_{perm.model}_{perm.action}" for perm in profile.permissions
        ]
    else:
        permissions = []
    access_expire_in = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_expire_timestamp = int(access_expire_in.timestamp())
    encode = {
        "iat": datetime.now().timestamp(),
        "exp": access_expire_timestamp,
        "sub": user.id,
        "type": "access",
        "profile": profile.name if profile else "Super User",
        "profileId": profile.id if profile else "",
        "clinic": user.clinic.company_name if user.clinic else "",
        "clinicId": user.clinic.id if user.clinic_id else "",
        "email": user.email,
        "fullName": user.full_name,
        "permissions": permissions,
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    refresh_expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_expire_timestamp = int(refresh_expire.timestamp())
    refresh_encode = {
        "iat": datetime.now().timestamp(),
        "exp": refresh_expire_timestamp,
        "sub": user.id,
        "type": "refresh",
        "profile": profile.name if profile else "Super User",
        "profileId": profile.id if profile else "",
        "clinic": user.clinic.company_name if user.clinic else "",
        "clinicId": user.clinic.id if user.clinic_id else "",
        "email": user.email,
        "fullName": user.full_name,
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
        old_token.refresh_expires_at = refresh_expire
        await old_token.save()
    return {
        "accessToken": token,
        "refreshToken": refresh_token,
        "tokenType": "Bearer",
        "expiresAt": access_expire_timestamp,
    }


def token_is_valid(token: Union[TokenModel, dict, str]) -> bool:
    """Verifies token validity"""
    if token and isinstance(token, TokenModel):
        return token.expires_at > datetime.now(tz=token.expires_at.tzinfo)
    if isinstance(token, dict) and token and "exp" in token:
        return token["exp"] > datetime.now().timestamp() and token["type"] == "access"
    if isinstance(token, str):
        try:
            token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            return (
                token_decoded["exp"] > datetime.now().timestamp()
                and token_decoded["type"] == "access"
            )
        except jwt.PyJWTError:
            return False
    return False


async def get_user_by_token(token: Union[str, dict]) -> Union[UserModel, None]:
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


async def login(
    email_or_username: str, password: str, clinic: Union[ClinicModel, None]
) -> Union[dict, None]:
    """Try login a user"""
    user = await UserModel.filter(
        Q(email=email_or_username) | Q(username=email_or_username)
    ).first()
    if not user or not password_is_correct(password, user.password):
        return None
    if (not user.profile or not clinic) and not user.is_superuser:
        return None
    if clinic and user.clinic != clinic:
        return None
    user.last_login_in = datetime.now()
    return await get_new_token(user)


async def logout(token: str, clinic: Union[ClinicModel, None]) -> None:
    """Logout a user"""
    try:
        token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user = await get_user_by_token(token_decoded)
        if not user and token_decoded["type"] != "access" and clinic != user.clinic:
            return
        old_token = await TokenModel.get(user=user)
        if not old_token:
            return
        old_token.delete()
    except jwt.PyJWTError:
        logger.warning("Failed logout")


async def get_refresh_token(
    token: str, clinic: Union[ClinicModel, None]
) -> Union[dict, None]:
    """Refresh token"""
    try:
        token_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user = await UserModel.get(id=token_decoded["sub"])
        if not user:
            return None
        if token_decoded["type"] != "refresh" and not token_is_valid(token):
            return None
        if clinic and user.clinic != clinic:
            return None
        return await get_new_token(user)
    except jwt.PyJWTError:
        return None

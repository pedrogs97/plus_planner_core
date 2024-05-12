"""Schemas for the auth app."""

from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr, Field

from src.base.enums import ActionEnum, ThemeEnum
from src.base.schemas import BaseSchema


class RefreshTokenSchema(BaseSchema):
    """Refresh token schema"""

    refresh_token: str = Field(alias="refreshToken")


class PermissionSerializerSchema(BaseSchema):
    """Permission schema"""

    id: int
    module: str
    model: str
    action: ActionEnum
    description: str


class ProfileSerializerSchema(BaseSchema):
    """
    Profile schema

    ProfileModel representation for response
    """

    id: int
    name: str
    permissions: List[PermissionSerializerSchema]


class ShortProfileSerializerSchema(BaseSchema):
    """
    Short Profile schema

    ProfileModel representation for response
    """

    id: int
    name: str


class UpdateUserSchema(BaseSchema):
    """
    User schema

    Used to update
    """

    profile_id: Optional[int] = Field(alias="profileId", default=None)
    full_name: Optional[str] = Field(alias="fullName", default=None)
    username: Optional[str] = None
    email: Optional[str] = None
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    phone: Optional[str] = None
    theme: Optional[ThemeEnum] = ThemeEnum.LIGHT
    is_active: Optional[bool] = Field(alias="isActive", default=None)
    is_clinic_master: bool = Field(alias="isClinicMaster", default=False)


class UserChangePasswordSchema(BaseSchema):
    """
    User change password schema

    Change only password
    """

    password: str
    current_password: str = Field(alias="currentPassword")


class UserSerializerSchema(BaseSchema):
    """
    User serializer

    UserModel representation for response
    """

    id: int
    profile: ShortProfileSerializerSchema
    full_name: str = Field(serialization_alias="fullName")
    username: str
    email: str
    is_active: bool = Field(serialization_alias="isActive")
    last_login_in: Optional[str] = Field(serialization_alias="lastLoginIn")
    theme: ThemeEnum
    profile_picture_path: Optional[str] = Field(
        serialization_alias="profilePicturePath", default=None
    )


class UserListSerializerSchema(BaseSchema):
    """
    User serializer

    UserModel representation for response
    """

    id: int
    profile: str
    profile_id: int = Field(serialization_alias="profileId")
    full_name: str = Field(serialization_alias="fullName")
    username: str
    email: str
    is_active: bool = Field(serialization_alias="isActive")
    last_login_in: Optional[str] = Field(
        serialization_alias="lastLoginIn", default=None
    )


class NewUpdateProfileSchema(BaseSchema):
    """New and Update profile schema"""

    name: Optional[str] = None
    permissionsIds: Optional[List[int]] = Field(
        alias="permissionsIds", serialization_alias="permissions_ids", default=[]
    )


class NewUserSchema(BaseSchema):
    """New user schema"""

    profile_id: Optional[int] = Field(alias="profileId")
    clinic_id: int = Field(alias="clinicId")
    username: str
    email: EmailStr
    taxpayer_id: str = Field(alias="taxpayerId")
    full_name: str = Field(alias="fullName")
    phone: Optional[str] = None
    is_clinic_master: bool = Field(alias="isClinicMaster", default=False)


class TokenSchema(BaseSchema):
    """Token schema"""

    id: Optional[int]
    user: UserSerializerSchema
    token: str
    expires_in: datetime = Field(serialization_alias="expiresIn")


class NewPasswordSchema(BaseSchema):
    """New password schema"""

    user_id: int = Field(serialization_alias="userId")


class NewUpdateClinicSchema(BaseSchema):
    """New and Update clinic schema"""

    company_name: str
    address: str
    phone: str
    email: str
    company_register_number: str = Field(alias="companyRegisterNumber")
    legal_entity: Optional[bool] = Field(alias="legalEntity", default=False)


class ClinicSerializerSchema(BaseSchema):
    """Clinic serializer schema"""

    id: int
    company_name: str = Field(serialization_alias="companyName")
    address: str
    phone: str
    email: str
    company_register_number: str = Field(serialization_alias="companyRegisterNumber")
    legal_entity: bool = Field(serialization_alias="legalEntity")
    users: List[UserListSerializerSchema]

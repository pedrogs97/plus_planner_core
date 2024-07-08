"""Schemas for the auth app."""

from typing import List, Optional

from plus_db_agent.enums import ActionEnum, ThemeEnum
from plus_db_agent.schemas import BaseSchema
from pydantic import EmailStr, Field, field_validator

from src.manager.repository import (
    ClinicRepository,
    PermissionRepository,
    ProfileRepository,
)


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

    profile: Optional[int] = None
    full_name: Optional[str] = Field(alias="fullName", default=None)
    username: Optional[str] = None
    email: Optional[str] = None
    taxpayer_id: Optional[str] = Field(alias="taxpayerId", default=None)
    phone: Optional[str] = None
    theme: Optional[ThemeEnum] = ThemeEnum.LIGHT
    is_active: Optional[bool] = Field(alias="isActive", default=None)
    is_clinic_master: bool = Field(alias="isClinicMaster", default=False)

    @field_validator("profile")
    @classmethod
    async def validate_profile(cls, profile: int):
        """Validate profile ID"""
        if profile < 1:
            raise ValueError("ID do perfil inválido")

        profile_db = await ProfileRepository().get_by_id(profile)
        if not profile_db:
            raise ValueError("Perfil não encontrado")
        return profile


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
    permissions: Optional[List[int]] = []

    @field_validator("permissions")
    @classmethod
    async def validate_permissions(cls, permissions: List[int]):
        """Validate permissions ids"""
        for permission_id in permissions:
            if permission_id < 1:
                raise ValueError(f"ID da permissão inválido. ID: {permission_id}")
            permission_db = await PermissionRepository().get_by_id(permission_id)
            if not permission_db:
                raise ValueError(f"Permissão não encontrada. ID: {permission_id}")
        return permissions


class NewUserSchema(BaseSchema):
    """New user schema"""

    profile: Optional[int]
    clinic: int
    username: str
    email: EmailStr
    taxpayer_id: str = Field(alias="taxpayerId")
    full_name: str = Field(alias="fullName")
    phone: Optional[str] = None
    is_clinic_master: bool = Field(alias="isClinicMaster", default=False)

    @field_validator("profile")
    @classmethod
    async def validate_profile(cls, profile: int):
        """Validate profile ID"""
        if profile < 1:
            raise ValueError("ID do perfil inválido")

        profile_db = await ProfileRepository().get_by_id(profile)
        if not profile_db:
            raise ValueError("Perfil não encontrado")
        return profile

    @field_validator("clinic")
    @classmethod
    async def validate_clinic(cls, clinic: int):
        """Validate clinic ID"""
        if clinic < 1:
            raise ValueError("ID da clínica inválido")

        clinic_db = await ClinicRepository().get_by_id(clinic)
        if not clinic_db:
            raise ValueError("Clínica não encontrada")
        return clinic


class NewUpdateClinicSchema(BaseSchema):
    """New and Update clinic schema"""

    company_name: str = Field(alias="companyName")
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
    logo_path: Optional[str] = Field(serialization_alias="logoPath")
    header_quarter: Optional[str] = Field(serialization_alias="headerQuarter")

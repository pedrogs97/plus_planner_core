"""Auth service"""

import random
from typing import List

from fastapi.security import APIKeyHeader
from fastapi_pagination import Page
from plus_db_agent.config import bcrypt_context
from plus_db_agent.filters import BaseFilter, PaginationFilter
from plus_db_agent.models import BaseModel, ClinicModel, ProfileModel, UserModel
from plus_db_agent.schemas import BaseSchema
from plus_db_agent.service import GenericService
from tortoise.expressions import Q

from src.manager.controller import ClinicController, ProfileController, UserController
from src.manager.schemas import (
    ClinicSerializerSchema,
    ProfileSerializerSchema,
    UserSerializerSchema,
)


class UserService(GenericService):
    """User service"""

    def __init__(self) -> None:
        self.oauth2_scheme = APIKeyHeader(name="Authorization")
        self.model = UserModel
        self.controller = UserController()
        self.module_name = "user"
        self.serializer = UserSerializerSchema

    def __generate_random_password(self) -> str:
        """Generate random password"""
        return "".join(
            random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(12)
        )

    def hash_password(self, password: str) -> str:
        """Hash password"""
        return bcrypt_context.hash(password)

    def password_is_correct(self, password: str, hashed_password: str) -> bool:
        """Verify if password is correct"""
        return bcrypt_context.verify(password, hashed_password)

    async def request_reset_password(self, email: str) -> bool:
        """Request reset password"""
        user = await self.controller.get_by_field("email", email)
        if not user:
            return False
        # TODO: Implement email service
        return True

    async def reset_password(
        self, user: UserModel, new_password: str, authenticated_user: UserModel
    ) -> bool:
        """Reset password"""
        dict_to_update = {
            "password": self.hash_password(new_password),
        }
        await self.controller.update(dict_to_update, user.id, authenticated_user)
        return True

    async def change_password(
        self,
        user: UserModel,
        old_password: str,
        new_password: str,
        authenticated_user: UserModel,
    ) -> bool:
        """Change password"""
        if not self.password_is_correct(old_password, user.password):
            return False

        dict_to_update = {
            "password": self.hash_password(new_password),
        }
        await self.controller.update(dict_to_update, user.id, authenticated_user)
        return True

    async def add(
        self, record: dict, authenticated_user: UserModel
    ) -> UserSerializerSchema:
        """Create a user"""
        new_random_password = self.__generate_random_password()
        new_user_dict = {
            **record,
            "password": self.hash_password(new_random_password),
        }
        # TODO: Implement email service to send password
        new_user = await self.controller.add(new_user_dict, authenticated_user)
        return self.serializer_obj(new_user, UserSerializerSchema)


class ProfileService(GenericService):
    """Profile service"""

    def __init__(self) -> None:
        self.model = ProfileModel
        self.controller = ProfileController()
        self.serializer = ProfileSerializerSchema
        self.module_name = "profile"

    async def list(self, **filters) -> List[BaseSchema]:
        authenticated_user = filters.pop("authenticated_user")
        super_list = await super().list(clinic=authenticated_user.clinic, **filters)
        return [{"id": profile.id, "name": profile.name} for profile in super_list]


class ClinicService(GenericService):
    """Clinic service"""

    def __init__(self) -> None:
        self.model = ClinicModel
        self.controller = ClinicController()
        self.serializer = ClinicSerializerSchema
        self.module_name = "clinic"

    async def paginated_list(
        self, list_filters: BaseFilter, page_filter: PaginationFilter, **kwargs
    ) -> Page[BaseModel]:
        authenticated_user = kwargs.pop("authenticated_user")
        if authenticated_user.is_clinic_master:
            queryset = self.model.filter(
                Q(head_quarter=authenticated_user.clinic)
                | Q(id=authenticated_user.clinic.id)
            )
        else:
            queryset = self.model.filter(
                Q(head_quarter=authenticated_user.clinic.head_quarter)
                | Q(id=authenticated_user.clinic.head_quarter.id)
            )
        user_list = await list_filters.filter(queryset.filter(deleted=False, **kwargs))
        user_list = await self.serializer_list(user_list.all())
        return page_filter.paginate(user_list)

    async def list(self, **filters) -> List[BaseSchema]:
        authenticated_user: UserModel = filters.pop("authenticated_user")
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

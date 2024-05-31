"""Auth service"""

import random

from fastapi.security import OAuth2PasswordBearer
from plus_db_agent.config import bcrypt_context
from plus_db_agent.controller import GenericController
from plus_db_agent.models import UserModel
from plus_db_agent.service import GenericService

from src.auth.schemas import UserSerializerSchema


class UserService(GenericService):
    """User service"""

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")
    model = UserModel
    controller = GenericController()
    module_name = "auth"
    serializer = UserSerializerSchema

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

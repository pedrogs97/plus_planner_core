"""Repository class for the user model"""

from typing import Optional

from plus_db_agent.models import ClinicModel, ProfileModel, UserModel
from plus_db_agent.repository import GenericRepository


class UserRepository(GenericRepository):
    """User repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = UserModel

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by its email"""
        return await self.model.get_or_none(email=email)

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """Get a user by its username"""
        return await self.model.get_or_none(username=username)


class ProfileRepository(GenericRepository):
    """Profile repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = ProfileModel


class ClinicRepository(GenericRepository):
    """Clinic repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = ClinicModel

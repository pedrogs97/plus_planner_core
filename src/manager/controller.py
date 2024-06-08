"""User controller module"""

from plus_db_agent.controller import GenericController
from plus_db_agent.models import ClinicModel, ProfileModel, UserModel

from src.manager.repository import ClinicRepository, ProfileRepository, UserRepository
from src.manager.schemas import (
    ClinicSerializerSchema,
    ProfileSerializerSchema,
    UserSerializerSchema,
)


class UserController(GenericController):
    """User controller class"""

    def __init__(self) -> None:
        self.model = UserModel
        self.serializer = UserSerializerSchema
        self.repository = UserRepository()


class ProfileController(GenericController):
    """Profile controller class"""

    def __init__(self) -> None:
        self.model = ProfileModel
        self.serializer = ProfileSerializerSchema
        self.repository = ProfileRepository()


class ClinicController(GenericController):
    """Clinic controller class"""

    def __init__(self) -> None:
        self.model = ClinicModel
        self.serializer = ClinicSerializerSchema
        self.repository = ClinicRepository()

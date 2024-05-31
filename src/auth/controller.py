"""User controller module"""

from plus_db_agent.controller import GenericController

from src.auth.schemas import UserSerializerSchema
from src.auth.service import UserService


class UserController(GenericController):
    """User controller class"""

    service = UserService()
    serializer = UserSerializerSchema

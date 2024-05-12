"""Log services"""
import logging

from tortoise.exceptions import IntegrityError

from src.auth.models import UserModel
from src.log.models import LogModel

logger = logging.getLogger(__name__)


class LogService:
    """Log services"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(LogService, cls).__new__(cls)
        return cls._instance

    def set_log(
        self,
        module: str,
        model: str,
        operation: str,
        identifier: int,
        user: UserModel,
    ) -> bool:
        """Set a log from a operation"""
        try:
            new_log = LogModel(
                user=user,
                module=module,
                model=model,
                operation=operation,
                identifier=identifier,
            )
            new_log.save()
            return True
        except IntegrityError as error:
            logger.error("Error setting log: %s", error)
            return False

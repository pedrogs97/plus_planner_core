"""Base test module."""

import asyncio

import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError, OperationalError

from src.config import TORTOISE_ORM_TEST
from src.main import appAPI
from src.manager.models import UserModel
from src.manager.services import UserService


class TestBase:
    """Base test class."""

    test_client = TestClient(appAPI)
    user_service = UserService()

    @pytest.fixture(scope="session", autouse=True)
    async def set_up(self, request):
        """Set up test."""

        async def _init_db() -> None:
            try:
                await Tortoise._drop_databases()
            except (DBConnectionError, OperationalError):  # pragma: nocoverage
                pass

            await Tortoise.init(config=TORTOISE_ORM_TEST, _create_db=True)
            await Tortoise.generate_schemas(safe=False)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_init_db())

        request.addfinalizer(
            lambda: loop.run_until_complete(Tortoise._drop_databases())
        )

    @pytest.fixture
    async def common_user(self):
        """Create a user."""
        await UserModel.create(
            full_name="Admin",
            password=self.user_service.hash_password("admin"),
            username="admin",
            email="admin.test@email.com",
            taxpayer_id="12345678901",
            phone="12345678901",
        )

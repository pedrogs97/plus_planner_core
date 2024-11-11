"""Configuration for the tests."""

import asyncio
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError, OperationalError

from src.auth.service import hash_password
from src.config import ACCESS_TOKEN_EXPIRE_HOURS

DATABASE_CONFIG_TEST = {
    "connections": {"default": "sqlite://:memory:"},
    "apps": {
        "core": {
            "models": [
                "plus_db_agent.models",
            ],
            "default_connection": "default",
        },
    },
}


async def _init_db() -> None:
    try:
        await Tortoise.init(config=DATABASE_CONFIG_TEST)
        await Tortoise._drop_databases()
    except (DBConnectionError, OperationalError):  # pragma: nocoverage
        pass

    await Tortoise.init(config=DATABASE_CONFIG_TEST, _create_db=True)
    await Tortoise.generate_schemas(safe=False)


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    """Initialize the test database."""

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_init_db())

    request.addfinalizer(lambda: loop.run_until_complete(Tortoise._drop_databases()))


@pytest_asyncio.fixture(scope="session")
async def user_fixture():
    """Fixture for user data."""
    from plus_db_agent.models import (  # pylint: disable=import-outside-toplevel
        UserModel,
    )

    user, _ = await UserModel.get_or_create(
        defaults={
            "email": "teste@email.com",
            "password": hash_password("password"),
            "username": "teste",
            "taxpayer_id": "123456789",
            "full_name": "Teste Testando",
            "is_superuser": True,
        }
    )
    yield user
    await user.delete()


@pytest_asyncio.fixture(scope="session")
async def token_valid_fixture(user_fixture):
    """Fixture for token data."""
    from plus_db_agent.models import (  # pylint: disable=import-outside-toplevel
        TokenModel,
    )

    access_expire_in = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    old_token = await TokenModel.get_or_none(user=user_fixture)
    if old_token:
        await old_token.delete()

    token = await TokenModel.create(
        user=user_fixture,
        token="token",
        refresh_token="refresh_token",
        expires_at=access_expire_in,
        refresh_expires_at=access_expire_in,
    )
    yield token
    await token.delete()


@pytest_asyncio.fixture(scope="session")
async def token_invalid_fixture(user_fixture):
    """Fixture for token data."""
    from plus_db_agent.models import (  # pylint: disable=import-outside-toplevel
        TokenModel,
    )

    access_expire_in = datetime.now() - timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    old_token = await TokenModel.get_or_none(user=user_fixture)
    if old_token:
        await old_token.delete()
    token = await TokenModel.create(
        user=user_fixture,
        token="token",
        refresh_token="refresh_token",
        expires_at=access_expire_in,
        refresh_expires_at=access_expire_in,
    )
    yield token
    await token.delete()

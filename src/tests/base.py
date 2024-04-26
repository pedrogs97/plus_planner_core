"""Base test module."""
import os

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

from src.auth.models import UserModel
from src.main import appAPI


class TestBase:
    """Base test class."""

    test_client = TestClient(appAPI)

    @pytest.fixture(scope="session", autouse=True)
    def set_up(self, request):
        """Set up test."""
        db_url = os.environ.get("TORTOISE_TEST_DB", "sqlite://:memory:")
        initializer(["tests.testmodels"], db_url=db_url, app_label="models")
        request.addfinalizer(finalizer)

    @pytest.fixture
    def common_user(self):
        """Create a user."""
        UserModel.create(
            full_name="Admin",
            password="admin",
            username="admin",
            email="admin.test@email.com",
            taxpayer_id="12345678901",
            phone="12345678901",
        )

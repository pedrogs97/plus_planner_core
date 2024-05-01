"""Test auth service."""
from src.config import BASE_API
from src.tests.base import TestBase


class TestAuth(TestBase):
    """Test auth service."""

    def test_login(self, common_user):
        """Test login."""
        expected_keys = [
            "access_token",
            "refresh_token",
            "token_type",
            "expires_in",
            "refresh_expires_in",
        ]
        response = self.test_client.post(
            f"{BASE_API}/auth/login",
            data={
                "username": "admin",
                "password": "admin",
            },
        )
        json_data = response.json()
        assert response.status_code == 200
        assert any(key in json_data for key in expected_keys)

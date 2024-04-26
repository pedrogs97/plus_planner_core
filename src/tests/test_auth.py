from src.tests.base import TestBase


class TestAuth(TestBase):
    """Test auth service."""

    def test_login(self):
        """Test login."""
        expected_keys = [
            "access_token",
            "refresh_token",
            "token_type",
            "expires_in",
            "refresh_expires_in",
            "profile",
            "full_name",
            "email",
            "permissions",
        ]
        response = self.test_client.post(
            "/auth/login",
            json={
                "email_or_username": "admin",
                "password": "admin",
            },
        )
        json_data = response.json()
        assert response.status_code == 200
        assert any(key in json_data for key in expected_keys)

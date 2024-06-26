"""API Client"""

from typing import Union

import requests
from plus_db_agent.models import UserModel

from src.config import AUTH_API_KEY, AUTH_API_URL


class APIClient:
    """API Client"""

    def __init__(self):

        if not AUTH_API_URL:
            raise ValueError("AUTH_API_URL not set")

        if not AUTH_API_KEY:
            raise ValueError("AUTH_API_KEY not set")

    def check_is_token_is_valid(self, token: str) -> bool:
        """Check if token is valid"""
        url = f"{AUTH_API_URL}/auth/check-token/"
        headers = {"X-API-Key": AUTH_API_KEY, "Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=500)
        return response.status_code == 200 and response.json()

    async def get_user_by_token(self, token: str) -> Union[UserModel, None]:
        """Check if token is valid"""
        url = f"{AUTH_API_URL}/auth/user/by-token/"
        headers = {"X-API-Key": AUTH_API_KEY, "Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=500)
        json_data = response.json()
        return (
            await UserModel.get_or_none(id=json_data.get("user")) if json_data else None
        )

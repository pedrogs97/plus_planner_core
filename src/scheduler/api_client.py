"""API Client"""

from datetime import datetime
from typing import Optional

import requests
from plus_db_agent.models import HolidayModel

from src.config import INVERTEXTO_TOKEN
from src.enums import Ufs


class APIClient:
    """API Client"""

    def __init__(self):
        if not INVERTEXTO_TOKEN:
            raise ValueError("INVERTEXTO_TOKEN not set")

    async def __save_holidays(self, holidays: dict) -> None:
        """Save holidays in the database"""
        await HolidayModel.create(
            **holidays, date=datetime.strptime(holidays["date"], "%Y-%m-%d")
        )

    def get_current_year_holidays(self, state: Optional[Ufs] = None) -> bool:
        """Get current year holidays"""
        try:
            current_year = datetime.now().year
            url = f"https://api.invertexto.com/v1/holidays/{current_year}"
            if state:
                url += f"?state={state.value}"
            headers = {"Authorization": f"Bearer {INVERTEXTO_TOKEN}"}
            response = requests.get(url, headers=headers, timeout=500)
            success = response.status_code == 200
            if success:
                self.__save_holidays(response.json())
            return success
        except Exception:  # pylint: disable=broad-except
            return False

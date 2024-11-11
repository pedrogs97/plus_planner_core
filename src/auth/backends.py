"""Application dependence classes"""

from fastapi import Request
from plus_db_agent.models import ClinicModel


class ClinicByHost:
    """Dependence class for get clinic by host"""

    async def __call__(
        self,
        request: Request,
    ) -> None:
        host = request.headers.get("host")
        if not host:
            request.state.clinic = None
            return
        if "127.0.0.1" in host:
            request.state.clinic = None
            return

        subdomain = host.split(".")[0]
        clinic = await ClinicModel.get_or_none(subdomain=subdomain)
        request.state.clinic = clinic

"""Custom ClientWebSocket"""

from fastapi import WebSocket


class ClientWebSocket(WebSocket):

    token: str
    clinic_id: int

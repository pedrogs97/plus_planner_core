""""""

from typing import List
from typing_extensions import Self
from src.scheduler.client import ClientWebSocket


class ConnectionManager:
    """Class defining socket events"""

    _instance: "ConnectionManager" = None
    client_connections: List[ClientWebSocket] = []

    def __new__(cls) -> Self:
        """Singleton instance"""
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance

    async def connect(self, websocket: ClientWebSocket):
        """Add a new client connection to the list on connect"""
        await websocket.accept()
        self.client_connections.append(websocket)

    async def send_personal_message(self, message: str, websocket: ClientWebSocket):
        """Direct Message"""
        await websocket.send_text(message)

    def disconnect(self, websocket: ClientWebSocket):
        """Remove a client connection from the list on disconnect"""
        self.client_connections.remove(websocket)

    async def listenner(self, websocket_client: ClientWebSocket) -> None:
        while True:
            data = await websocket_client.receive_text()
            print(data)

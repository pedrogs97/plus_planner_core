"""Custom ClientWebSocket"""

from typing import Iterable, Optional, Tuple, Union

from fastapi import WebSocket

from src.enums import MessageType
from src.wait_list.schemas import CreateUUIDSchema, ErrorResponseSchema, Message


class ClientWebSocket(WebSocket):
    """Custom ClientWebSocket"""

    token: Optional[str] = None
    clinic_id: int
    uuid: str

    async def accept(
        self,
        subprotocol: Union[str, None] = None,
        headers: Union[Iterable[Tuple[bytes, bytes]], None] = None,
        client_id: Union[int, None] = None,
        uuid_code: Union[str, None] = None,
    ) -> None:
        await super().accept(subprotocol, headers)
        if client_id is None or uuid_code is None:
            return await self.send_error_message("Client ID ou UUID não informado")
        self.clinic_id = client_id
        self.uuid = uuid_code

    async def send_invalid_message(self) -> None:
        """Send invalid message"""
        await self.send(
            Message(message_type=MessageType.INVALID, clinic_id=self.clinic_id)
        )

    async def send_error_message(self, error: str) -> None:
        """Send error message"""
        await self.send(
            Message(
                message_type=MessageType.ERROR,
                clinic_id=self.clinic_id,
                data=ErrorResponseSchema(error=error),
            )
        )

    async def send_new_uuid(self, uuid_code: str) -> None:
        """Send new uuid"""
        await self.send(
            Message(
                message_type=MessageType.CREATE_UUID,
                clinic_id=self.clinic_id,
                data=CreateUUIDSchema(uuid=uuid_code),
            )
        )

    async def send(self, message: Message) -> None:
        """Send message"""
        await self.send_json(message.model_dump())

"""Connection Manager Module"""

import asyncio
import json
import logging
import time
import uuid
from threading import Thread
from typing import List

from fastapi.websockets import WebSocketDisconnect
from plus_db_agent.enums import SchedulerStatus
from tortoise.exceptions import OperationalError
from typing_extensions import Self

from src.client import APIClient
from src.enums import MessageType
from src.manager.repository import ClinicRepository
from src.wait_list.client import ClientWebSocket
from src.wait_list.schemas import (
    ConnectionSchema,
    Message,
    NewPatientInWaitSchema,
    PatientWaitListSchema,
    UpdatePatientInWaitSchema,
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Class defining socket events"""

    _instance: "ConnectionManager" = None
    client_connections: List[ClientWebSocket] = []
    queue = asyncio.Queue()
    wait_list: List[PatientWaitListSchema] = []
    api_client = APIClient()
    clinic_repositoty = ClinicRepository()

    def __new__(cls) -> Self:
        """Singleton instance"""
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance

    async def connect(self, websocket: ClientWebSocket, clinic_id: int):
        """Add a new client connection to the list on connect"""
        if self.clinic_repositoty.get_by_id(clinic_id):
            new_uuid = uuid.uuid4().hex
            await websocket.accept(clinic_id=clinic_id, new_uuid=new_uuid)
            await websocket.send_new_uuid(new_uuid)
            self.client_connections.append(websocket)
            self.__listenner(websocket)
        else:
            await websocket.send_error_message("Token inválido ou clínica inexistente")
            time.sleep(0.1)
            await websocket.close()

    async def disconnect(self, client: ClientWebSocket):
        """Remove a client connection from the list on disconnect"""
        if client in self.client_connections:
            self.client_connections.remove(client)
        if client.state == "open":
            await client.close()

    def get_all_connections(self) -> List[ClientWebSocket]:
        """Return all connections"""
        return self.client_connections

    def get_connection_by_uuid(self, uuid_code: str) -> ClientWebSocket:
        """Return connection by uuid"""
        for connection in self.client_connections:
            if connection.uuid == uuid_code:
                return connection
        return None

    def get_connection_by_clinic_id(self, clinic_id: int) -> ClientWebSocket:
        """Return connection by clinic_id"""
        for connection in self.client_connections:
            if connection.clinic_id == clinic_id:
                return connection
        return None

    async def broadcast_clinic_messages(self, clinic_id: int, message: Message) -> None:
        """Broadcast messages"""
        for client_connection in self.client_connections:
            if client_connection.clinic_id == clinic_id:
                await client_connection.send(message)

    async def __listenner(self, websocket_client: ClientWebSocket) -> None:
        """Listen to incoming messages"""
        try:
            while True:
                data = await websocket_client.receive_json()
                try:
                    message = Message.model_validate_json(json.dumps(data))
                    await self.queue.put((websocket_client, message))
                except (ValueError, AttributeError):
                    await websocket_client.send_invalid_message()
                    continue
        except WebSocketDisconnect:
            self.disconnect(websocket_client)

    async def __process_enqueue_wait_list(
        self, message: Message, client: ClientWebSocket
    ):
        """Process enqueue wait list"""
        try:
            if not isinstance(message.data, NewPatientInWaitSchema):
                await client.send_invalid_message()
                return
            patient_id = message.data.patient_id
            await self.wait_list.append(
                PatientWaitListSchema(
                    patient_id=patient_id, status=SchedulerStatus.WAITING
                )
            )
            await client.send(
                Message(
                    message_type=MessageType.NEW_PATIENT_IN_WAIT,
                    clinic_id=message.clinic_id,
                    data=NewPatientInWaitSchema(patient_id=patient_id),
                )
            )
        except (OperationalError, AttributeError):
            await client.send_error_message("Erro ao adicionar paciente na fila")

    async def __process_update_wait_list(
        self, message: Message, client: ClientWebSocket
    ):
        """Process update wait list"""
        try:
            if not isinstance(message.data, UpdatePatientInWaitSchema):
                await client.send_invalid_message()
                return
            patient_id = message.data.patient_id
            if (
                message.data.status == SchedulerStatus.CANCELED
                or message.data.status == SchedulerStatus.DONE
            ):
                self.wait_list = [
                    patient
                    for patient in self.wait_list
                    if patient.patient_id != patient_id
                ]
            await client.send(
                Message(
                    message_type=MessageType.UPDATE_PATIENT_IN_WAIT,
                    clinic_id=message.clinic_id,
                    data=None,
                )
            )
        except (OperationalError, AttributeError):
            await client.send_error_message("Erro ao atualizar paciente na fila")

    async def __process_call_next_patient(
        self, message: Message, client: ClientWebSocket
    ):
        """Process call next patient"""
        try:
            if not self.wait_list:
                await client.send_error_message("Fila vazia")
                return
            next_patient = self.wait_list.pop(0)
            await client.send(
                Message(
                    message_type=MessageType.NEXT_PATIENT_IN_WAIT,
                    clinic_id=message.clinic_id,
                    data=PatientWaitListSchema(
                        patient_id=next_patient.patient_id,
                        status=SchedulerStatus.DONE,
                        created_at=next_patient.created_at,
                    ),
                )
            )
        except (OperationalError, AttributeError):
            await client.send_error_message("Erro ao chamar próximo")

    async def __process_wait_list(self, client: ClientWebSocket):
        """Process wait list"""
        try:
            await client.send(
                Message(
                    message_type=MessageType.NEXT_PATIENT_IN_WAIT,
                    clinic_id=client.clinic_id,
                    data=self.wait_list,
                )
            )
        except (OperationalError, AttributeError):
            await client.send_error_message("Erro ao buscar lista de espera")

    async def __process_connection(self, message: Message, client: ClientWebSocket):
        """Process connection"""
        try:
            if not isinstance(message.data, ConnectionSchema):
                await client.send_invalid_message()
                return
            if not self.api_client.check_is_token_is_valid(message.data.token):
                await client.send_error_message("Token inválido")
                time.sleep(0.1)
                await self.disconnect(client)
                return
            user_dict = self.api_client.get_user_by_token(client.token)
            client.token = message
            client.user_id = user_dict["id"]
            await client.send(
                Message(
                    message_type=MessageType.CONNECTION, clinic_id=message.clinic_id
                )
            )
        except (OperationalError, AttributeError):
            await client.send_error_message("Erro ao validar conexão")
            time.sleep(0.1)
            await self.disconnect(client)

    async def __process_message(
        self, message: Message, client: ClientWebSocket
    ) -> None:
        """Process message"""
        try:
            if message.message_type == MessageType.CONNECTION:
                await self.__process_connection(message, client)
            elif (
                client.token and message.message_type == MessageType.NEW_PATIENT_IN_WAIT
            ):
                await self.__process_enqueue_wait_list(message, client)
            elif (
                client.token
                and message.message_type == MessageType.UPDATE_PATIENT_IN_WAIT
            ):
                await self.__process_update_wait_list(message, client)
            elif (
                client.token
                and message.message_type == MessageType.NEXT_PATIENT_IN_WAIT
            ):
                await self.__process_call_next_patient(message, client)
            elif (
                client.token
                and message.message_type == MessageType.LIST_PATIENTS_IN_WAIT
            ):
                await self.__process_wait_list(client)
            elif not client.token:
                await client.send_error_message("Token inválido")
                time.sleep(0.1)
                await self.disconnect(client)
            else:
                await client.send_invalid_message()
        except (AttributeError, OperationalError):
            await client.send_error_message("Erro ao processar a mensagem")

    async def __process_queue(self):
        while True:
            if not self.queue.empty():
                websocket, message = await self.queue.get()
                logger.info("Processing message: %s", message.message_type)
                await self.__process_message(message, websocket)
            await asyncio.sleep(1)

    def __start_queue_processor(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__process_queue())

    def start_main_thread(self):
        """Start the main thread"""
        thread = Thread(target=self.__start_queue_processor)
        thread.start()
        logger.info("Main thread started")

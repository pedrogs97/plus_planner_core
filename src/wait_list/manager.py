"""Connection Manager Module"""

import asyncio
import time
from threading import Thread
from typing import List

from plus_db_agent.enums import SchedulerStatus
from plus_db_agent.queue import BaseConnectionManager
from tortoise.exceptions import OperationalError

from src.auth.service import get_user_by_token, token_is_valid
from src.enums import WaitListMessageType
from src.manager.repository import ClinicRepository
from src.wait_list.client import ClientWebSocket
from src.wait_list.logger import logger
from src.wait_list.schemas import (
    ConnectionSchema,
    Message,
    NewPatientInWaitSchema,
    PatientWaitListSchema,
    UpdatePatientInWaitSchema,
    WaitListMessage,
)


class ConnectionManager(BaseConnectionManager):
    """Class defining socket events"""

    wait_list: List[PatientWaitListSchema] = []
    clinic_repositoty = ClinicRepository()

    async def connect(self, websocket: ClientWebSocket, clinic_id: int):
        """Add a new client connection to the list on connect"""
        if self.clinic_repositoty.get_by_id(clinic_id):
            await super().connect(websocket, clinic_id)
        else:
            await websocket.send_error_message("Token inválido ou clínica inexistente")
            time.sleep(0.1)
            await websocket.close()

    async def __process_enqueue_wait_list(
        self, message: WaitListMessage, client: ClientWebSocket
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
                WaitListMessage(
                    message_type=WaitListMessageType.NEW_PATIENT_IN_WAIT,
                    clinic_id=message.clinic_id,
                    data=NewPatientInWaitSchema(patient_id=patient_id),
                )
            )
        except (OperationalError, AttributeError):
            await client.send_error_message("Erro ao adicionar paciente na fila")

    async def __process_update_wait_list(
        self, message: WaitListMessage, client: ClientWebSocket
    ):
        """Process update wait list"""
        try:
            if not isinstance(message.data, UpdatePatientInWaitSchema):
                await client.send_invalid_message()
                return
            patient_id = message.data.patient_id
            if message.data.status in [SchedulerStatus.CANCELED, SchedulerStatus.DONE]:
                self.wait_list = [
                    patient
                    for patient in self.wait_list
                    if patient.patient_id != patient_id
                ]
            await client.send(
                WaitListMessage(
                    message_type=WaitListMessageType.UPDATE_PATIENT_IN_WAIT,
                    clinic_id=message.clinic_id,
                    data=None,
                )
            )
        except (OperationalError, AttributeError):
            await client.send_error_message("Erro ao atualizar paciente na fila")

    async def __process_call_next_patient(
        self, message: WaitListMessage, client: ClientWebSocket
    ):
        """Process call next patient"""
        try:
            if not self.wait_list:
                await client.send_error_message("Fila vazia")
                return
            next_patient = self.wait_list.pop(0)
            await client.send(
                WaitListMessage(
                    message_type=WaitListMessageType.NEXT_PATIENT_IN_WAIT,
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
                WaitListMessage(
                    message_type=WaitListMessageType.NEXT_PATIENT_IN_WAIT,
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
            if not token_is_valid(message.data.token):
                await client.send_error_message("Token inválido")
                time.sleep(0.1)
                await self.disconnect(client)
                return
            user_dict = await get_user_by_token(client.token)
            if not user_dict:
                await client.send_error_message("Usuário não encontrado")
                time.sleep(0.1)
                await self.disconnect(client)
            client.token = message.data.token
            client.user_id = user_dict.id
            await client.send(
                WaitListMessage(
                    message_type=WaitListMessageType.CONNECTION,
                    clinic_id=message.clinic_id,
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
            if message.message_type == WaitListMessageType.CONNECTION:
                await self.__process_connection(message, client)
            elif (
                client.token
                and message.message_type == WaitListMessageType.NEW_PATIENT_IN_WAIT
            ):
                await self.__process_enqueue_wait_list(message, client)
            elif (
                client.token
                and message.message_type == WaitListMessageType.UPDATE_PATIENT_IN_WAIT
            ):
                await self.__process_update_wait_list(message, client)
            elif (
                client.token
                and message.message_type == WaitListMessageType.NEXT_PATIENT_IN_WAIT
            ):
                await self.__process_call_next_patient(message, client)
            elif (
                client.token
                and message.message_type == WaitListMessageType.LIST_PATIENTS_IN_WAIT
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
        logger.info("Wait list Main thread started")

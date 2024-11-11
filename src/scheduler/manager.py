"""Connection Manager Module"""

import asyncio
import time
from datetime import datetime
from threading import Thread

from plus_db_agent.enums import SchedulerStatus
from plus_db_agent.models import SchedulerModel
from plus_db_agent.queue import BaseConnectionManager
from plus_db_agent.schemas import BaseMessageType
from tortoise.exceptions import OperationalError

from src.auth.service import get_user_by_token, token_is_valid
from src.backends import check_clinic_id
from src.enums import SchedulerMessageType
from src.scheduler.api_client import APIClient
from src.scheduler.client import ClientWebSocket
from src.scheduler.logger import logger
from src.scheduler.schemas import (
    AddEventSchema,
    ConnectionSchema,
    EditEventSchema,
    EventSchema,
    GetDayCalendarSchema,
    GetFullMonthCalendarSchema,
    GetFullWeekCalendarSchema,
    Message,
    RemoveEventSchema,
    SchedulerMessage,
)
from src.utils import get_week


class ConnectionManager(BaseConnectionManager):
    """Class defining socket events"""

    api_client = APIClient()

    async def __process_full_month_calendar(
        self, message: SchedulerMessage, client: ClientWebSocket
    ) -> None:
        """Process full month calendar"""
        if not isinstance(message.data, GetFullMonthCalendarSchema):
            await client.send_invalid_message()
            return
        current_date = datetime.strptime(
            f"{message.data.year}-{message.data.month}-01", "%Y-%m-%d"
        ).date()
        scheduler_events = await SchedulerModel.filter(
            clinic_id=message.clinic_id,
            date__month=current_date.month,
            date__year=current_date.year,
        ).all()
        await client.send_events_calendar(scheduler_events)

    async def __process_full_week_calendar(
        self, message: SchedulerMessage, client: ClientWebSocket
    ) -> None:
        """Process full week calendar"""
        if not isinstance(message.data, GetFullWeekCalendarSchema):
            await client.send_invalid_message()
            return
        current_date = datetime.strptime(
            f"{message.data.year}-{message.data.month}-{message.data.day}", "%Y-%m-%d"
        ).date()
        week, _, _ = get_week(current_date)
        scheduler_events = await SchedulerModel.filter(
            clinic_id=message.clinic_id, date__gte=week[0], date__lte=week[-1]
        ).all()
        await client.send_events_calendar(scheduler_events)

    async def __process_day_calendar(
        self, message: SchedulerMessage, client: ClientWebSocket
    ) -> None:
        """Process day calendar"""
        if not isinstance(message.data, GetDayCalendarSchema):
            await client.send_invalid_message()
            return
        scheduler_events = await SchedulerModel.filter(
            clinic_id=message.clinic_id, date__date=message.data.date
        ).all()
        await client.send_events_calendar(scheduler_events)

    async def __process_add_event(
        self, message: SchedulerMessage, client: ClientWebSocket
    ) -> None:
        """Process add event"""
        try:
            if not isinstance(message.data, AddEventSchema):
                await client.send_invalid_message()
                return
            new_event = await SchedulerModel.create(
                status=SchedulerStatus.WAITING_CONFIRMATION.value,
                date=message.data.date,
                description=message.data.description,
                is_return=message.data.is_return,
                is_off=message.data.is_off,
                off_reason=message.data.off_reason,
                clinic_id=message.clinic_id,
                patient=message.data.patient,
                user=client.user_id,
                desk=message.data.desk,
            )
            new_event_schema = EventSchema(
                id=new_event.id,
                date=new_event.date,
                description=new_event.description,
                is_return=new_event.is_return,
                is_off=new_event.is_off,
                off_reason=new_event.off_reason,
                patient=new_event.patient,
                desk=new_event.desk,
            )
            new_message = SchedulerMessage(
                message_type=SchedulerMessageType.ADD_EVENT,
                clinic_id=message.clinic_id,
                data=new_event_schema,
            )
            await self.broadcast_clinic_messages(client.clinic_id, new_message)
        except (OperationalError, AttributeError):
            await client.send_error_message("Erro ao adicionar o evento")

    async def __process_edit_event(
        self, message: SchedulerMessage, client: ClientWebSocket
    ) -> None:
        """Process edit event"""
        try:
            if not isinstance(message.data, EditEventSchema):
                await client.send_invalid_message()
                return
            event = await SchedulerModel.get(id=message.data.event_id)
            for key, value in message.data.model_dump().items():
                if value and hasattr(event, key):
                    setattr(event, key, value)
            await event.save()
            new_event_schema = EventSchema(
                id=event.id,
                date=event.date,
                description=event.description,
                is_return=event.is_return,
                is_off=event.is_off,
                off_reason=event.off_reason,
                patient=event.patient,
                desk=event.desk,
            )
            new_message = SchedulerMessage(
                message_type=SchedulerMessageType.EDIT_EVENT,
                clinic_id=message.clinic_id,
                data=new_event_schema,
            )
            await self.broadcast_clinic_messages(client.clinic_id, new_message)
        except OperationalError:
            await client.send_error_message("Erro ao editar o evento")

    async def __process_remove_event(
        self, message: SchedulerMessage, client: ClientWebSocket
    ) -> None:
        """Process remove event"""
        try:
            if not isinstance(message.data, RemoveEventSchema):
                await client.send_invalid_message()
                return
            event = await SchedulerModel.get(id=message.data.event_id)
            await event.delete()
            new_message = SchedulerMessage(
                message_type=SchedulerMessageType.REMOVE_EVENT,
                clinic_id=message.clinic_id,
                data=message.data,
            )
            await self.broadcast_clinic_messages(client.clinic_id, new_message)
        except OperationalError:
            await client.send_error_message("Erro ao remover o evento")

    async def process_connection(self, message: Message, client: ClientWebSocket):
        """Process connection"""
        try:
            if (
                not isinstance(message.data, ConnectionSchema)
                or message.data.uuid != client.uuid
            ):
                await client.send_invalid_message()
                return
            if not token_is_valid(message.data.token):
                await client.send_error_message("Token inválido")
                time.sleep(0.1)
                await self.disconnect(client)
                return

            user = await get_user_by_token(client.token)

            if not user:
                await client.send_error_message("Usuário não encontrado")
                time.sleep(0.1)
                await self.disconnect(client)
                return

            if (
                not check_clinic_id(message.data.clinic_id)
                and user.clinic.id != message.data.clinic_id
            ):
                await client.send_error_message("Clínica não válida")
                time.sleep(0.1)
                await self.disconnect(client)
                return

            client.user_id = user.id
            client.token = message.data.token
            client.clinic_id = message.data.clinic_id
            await client.send(
                Message(
                    message_type=BaseMessageType.CONNECTION,
                    clinic_id=message.data.clinic_id,
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
            if message.message_type == SchedulerMessageType.CONNECTION:
                await self.process_connection(message, client)
            elif (
                client.token
                and message.message_type == SchedulerMessageType.GET_FULL_MONTH_CALENDAR
            ):
                await self.__process_full_month_calendar(message, client)
            elif (
                client.token
                and message.message_type == SchedulerMessageType.GET_FULL_WEEK_CALENDAR
            ):
                await self.__process_full_week_calendar(message, client)
            elif (
                client.token
                and message.message_type == SchedulerMessageType.GET_DAY_CALENDAR
            ):
                await self.__process_day_calendar(message, client)
            elif (
                client.token and message.message_type == SchedulerMessageType.ADD_EVENT
            ):
                await self.__process_add_event(message, client)
            elif (
                client.token and message.message_type == SchedulerMessageType.EDIT_EVENT
            ):
                await self.__process_edit_event(message, client)
            elif (
                client.token
                and message.message_type == SchedulerMessageType.REMOVE_EVENT
            ):
                await self.__process_remove_event(message, client)
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
                logger.info("Scheduler Processing message: %s", message.message_type)
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
        logger.info("Scheduler Main thread started")

""" Scheduler custom ClientWebSocket """

from typing import List

from plus_db_agent.models import SchedulerModel
from plus_db_agent.queue import BaseClientWebSocket

from src.enums import SchedulerMessageType
from src.scheduler.schemas import (
    EventSchema,
    ReponseEventsCalendarSchema,
    SchedulerMessage,
)


class ClientWebSocket(BaseClientWebSocket):
    """Scheduler custom ClientWebSocket"""

    async def send_events_calendar(self, events: List[SchedulerModel]) -> None:
        """Send full month calendar"""
        scheduler_events: List[EventSchema] = []
        for event in events:
            scheduler_events.append(
                EventSchema(
                    id=event.id,
                    date=event.date,
                    description=event.description,
                    is_return=event.is_return,
                    is_off=event.is_off,
                    off_reason=event.off_reason,
                    patient=event.patient,
                    desk=event.desk,
                )
            )
        await self.send(
            SchedulerMessage(
                messageType=SchedulerMessageType.GET_FULL_MONTH_CALENDAR,
                clinicId=self.clinic_id,
                data=ReponseEventsCalendarSchema(events=scheduler_events),
            )
        )

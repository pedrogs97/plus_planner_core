"""Scheduler service"""
from src.auth.models import UserModel
from src.scheduler.models import SchedulerModel
from src.scheduler.schemas import AddEventSchema


class SchedulerService:
    """Scheduler service"""

    async def add_event(
        self, new_event: AddEventSchema, authenticated_user: UserModel
    ) -> SchedulerModel:
        """Add a new event"""
        return await SchedulerModel.create(
            date=new_event.date,
            description=new_event.description,
            is_return=new_event.is_return,
            is_off=new_event.is_off,
            off_reason=new_event.off_reason,
            clinic_id=new_event.clinic_id,
            patient_id=new_event.patient_id,
            user_id=authenticated_user.id,
            desk_id=new_event.desk_id,
        )

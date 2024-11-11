"""Schemas for the scheduler module."""

from datetime import datetime
from typing import List, Optional, Union

from plus_db_agent.enums import SchedulerStatus
from plus_db_agent.schemas import BaseSchema, Message
from pydantic import Field

from src.enums import WaitListMessageType


class ConnectionSchema(BaseSchema):
    """Connection Schema"""

    token: str


class CreateUUIDSchema(BaseSchema):
    """Create UUID Schema"""

    uuid: str


class ErrorResponseSchema(BaseSchema):
    """Error Response Schema"""

    error: str


class NewPatientInWaitSchema(BaseSchema):
    """New Patient in wait Schema"""

    patient_id: int = Field(alias="patientId")


class UpdatePatientInWaitSchema(BaseSchema):
    """Update Patient in wait Schema"""

    patient_id: int = Field(alias="patientId")
    status: SchedulerStatus


class PatientWaitListSchema(BaseSchema):
    """Patient Wait List Schema"""

    patient_id: int = Field(alias="patientId")
    status: SchedulerStatus
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.now)


class WaitListMessage(Message):
    """Message Schema"""

    message_type: WaitListMessageType
    data: Optional[
        Union[
            ConnectionSchema,
            CreateUUIDSchema,
            ErrorResponseSchema,
            UpdatePatientInWaitSchema,
            NewPatientInWaitSchema,
            List[PatientWaitListSchema],
        ]
    ] = None

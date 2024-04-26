"""Schemas for the scheduler module."""
from datetime import datetime
from typing import Optional

from pydantic import Field, model_validator
from typing_extensions import Self

from src.auth.models import ClinicModel
from src.base.schemas import BaseSchema
from src.clinic_office.models import DeskModel


class AddEventSchema(BaseSchema):
    """Schema to add a new event"""

    date: datetime
    description: Optional[str] = ""
    is_return: Optional[bool] = Field(alias="isReturn", default=False)
    is_off: Optional[bool] = Field(alias="isOff", default=False)
    off_reason: Optional[str] = Field(alias="offReason", default=None)
    clinic_id: int
    patient_id: int
    user_id: int
    desk_id: int

    @model_validator(mode="after")
    def check_off_reason(self) -> Self:
        """Check if off_reason is informed when is_off is True."""
        if self.is_off and self.off_reason is None:
            raise ValueError("Informe o motivo da ausência.")
        return self

    @model_validator(mode="before")
    def check_date(self) -> Self:
        """Check if date is in the future."""
        if self.date < datetime.now():
            raise ValueError("A data do agendamento deve ser futura.")
        return self

    @model_validator(mode="before")
    def check_clinic(self) -> Self:
        """Check if clinic exists."""
        if not ClinicModel.filter(id=self.clinic_id).exists():
            raise ValueError("Clínica não encontrada.")
        return self

    @model_validator(mode="before")
    def check_desk(self) -> Self:
        """Check if desk exists."""
        desk = DeskModel.filter(id=self.desk_id).first()
        if not desk:
            raise ValueError("Consultório não encontrado.")

        if not desk.vacancy:
            raise ValueError("Consultório não disponível.")

        return self

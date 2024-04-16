from tortoise import fields
from src.base.models import BaseModel
from src.base.enums import SchedulerStatus


class SchedulerModel(BaseModel):
    """Model to represent a scheduler."""

    status = fields.CharEnumField(
        enum_type=SchedulerStatus,
        max_length=20,
        default=SchedulerStatus.WAITING_CONFIRMATION,
    )
    date = fields.DatetimeField()
    description = fields.TextField(null=True)
    is_return = fields.BooleanField(default=False)
    is_off = fields.BooleanField(default=False)
    off_reason = fields.TextField(null=True)
    clinic = fields.ForeignKeyField(
        "models.ClinicModel",
        related_name="schedulers",
        on_delete=fields.NO_ACTION,
    )
    patient = fields.ForeignKeyField(
        "models.PatientModel",
        related_name="schedulers",
        on_delete=fields.NO_ACTION,
    )
    user = fields.ForeignKeyField(
        "models.UserModel",
        related_name="schedulers",
        on_delete=fields.NO_ACTION,
    )
    desk = fields.ForeignKeyField(
        "models.DeskModel",
        related_name="schedulers",
        on_delete=fields.NO_ACTION,
    )

    def __str__(self):
        return f"{self.date} - {self.status}"

    class Meta:
        table = "schedulers"

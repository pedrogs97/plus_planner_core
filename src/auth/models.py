from tortoise import fields
from src.base.models import BaseModel

class UserModel(BaseModel):
    """Model to represent a user."""

    full_name = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    taxpayer_id = fields.CharField(max_length=12, unique=True)
    phone = fields.CharField(max_length=20, null=True)
    profile_picture_path = fields.CharField(max_length=255, null=True)
    is_clinic_master = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)

    def __str__(self):
        return self.full_name
    
    class Meta:
        table = "users"


class ProfileModel(BaseModel):
    """Model to represent a profile."""

    name = fields.CharField(max_length=255)
    clinic = fields.ForeignKeyField("models.ClinicModel", related_name="profiles", on_delete=fields.CASCADE)
    


class LinceseModel(BaseModel):
    """Model to represent a license."""

    license_number = fields.CharField(max_length=20)
    modules = fields.CharField(max_length=255)
    expiration_date = fields.DateField(null=True)

    def __str__(self):
        return f"{self.license_number}"
    
    class Meta:
        table = "licenses"

class ClinicModel(BaseModel):   
    """Model to represent a clinic."""

    head_quarters = fields.ForeignKeyField("models.ClinicModel", related_name="subsidiaries", on_delete=fields.CASCADE, null=True)
    license = fields.ForeignKeyField("models.LinceseModel", related_name="clinics", on_delete=fields.CASCADE)
    company_name = fields.CharField(max_length=255)
    company_register_number = fields.CharField(max_length=20)
    legal_entity = fields.CharField(max_length=255)
    address = fields.CharField(max_length=255)

    def __str__(self):
        return f"{self.company_name} - {self.legal_entity}"
    
    class Meta:
        table = "clinics"


class ClinicUserModel(BaseModel):
    """Model to represent the relationship between a clinic and a user."""

    clinic = fields.ForeignKeyField("models.ClinicModel", related_name="users", on_delete=fields.CASCADE)
    user = fields.ForeignKeyField("models.UserModel", related_name="clinics", on_delete=fields.CASCADE)

    def __str__(self):
        return f"{self.clinic} - {self.user}"
    
    class Meta:
        table = "clinic_users"
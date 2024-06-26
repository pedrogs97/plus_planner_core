"""Clinic office router"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from plus_db_agent.filters import PaginationFilter
from plus_db_agent.models import UserModel

from src.backends import PermissionChecker
from src.clinic_office.filters import PatientFilter
from src.clinic_office.schemas import (
    NewPatientSchema,
    PatientSerializerSchema,
    UpdatePatientSchema,
)
from src.clinic_office.service import PatientService
from src.config import NOT_ALLOWED

router = APIRouter(prefix="/clinic", tags=["Clinic Office"])
clinic_office_service = PatientService()


@router.get("/patients/", response_model=Page[PatientSerializerSchema])
async def get_patients(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "patients", "action": "view"}
            )
        ),
    ],
    patient_filters: PatientFilter = FilterDepends(PatientFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get all patients"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_office_service.paginated_list(
        patient_filters, page_filter, deteled=False
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/patients/", response_model=PatientSerializerSchema)
async def add_patient(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "patients", "action": "add"}
            )
        ),
    ],
    patient: NewPatientSchema,
):
    """Add a patient"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_office_service.add(
        patient.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)


@router.put("/patients/{patient_id}/", response_model=PatientSerializerSchema)
async def update_patient(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "patients", "action": "edit"}
            )
        ),
    ],
    patient_id: int,
    patient: UpdatePatientSchema,
):
    """Update a patient"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_office_service.update(
        patient.model_dump(by_alias=False), patient_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/patients/{patient_id}/", response_model=PatientSerializerSchema)
async def delete_patient(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "patients", "action": "delete"}
            )
        ),
    ],
    patient_id: int,
):
    """Delete a patient"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await clinic_office_service.delete(patient_id, authenticated_user)
    return JSONResponse(
        content={"message": "Patient deleted"}, status_code=status.HTTP_200_OK
    )


@router.get("/patients/{patient_id}/", response_model=PatientSerializerSchema)
async def get_patient(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "patients", "action": "view"}
            )
        ),
    ],
    patient_id: int,
):
    """Get a patient"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_office_service.get_obj_or_404(patient_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)

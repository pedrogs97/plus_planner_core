"""Clinic office router"""

import os
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from plus_db_agent.filters import PaginationFilter
from plus_db_agent.models import UserModel

from src.backends import PermissionChecker
from src.clinic_office.filters import (
    AnamnesisFilter,
    DeskFilter,
    PatientFilter,
    PlanFilter,
    QuestionFilter,
    SpecialtyFilter,
    TreatmentFilter,
    UrgencyFilter,
)
from src.clinic_office.schemas import (
    NewPatientSchema,
    NewUpdateAnamnesisSchema,
    NewUpdateDeskSchema,
    NewUpdateDocumentSchema,
    NewUpdatePlanSchema,
    NewUpdateQuestionSchema,
    NewUpdateSpecialtySchema,
    NewUpdateTreatmentSchema,
    NewUpdateUrgencySchema,
    PatientSerializerSchema,
    UpdatePatientSchema,
    UrgencySerializerSchema,
)
from src.clinic_office.service import (
    AnamnesisService,
    DeskService,
    DocumentService,
    PatientService,
    PlanService,
    QuestionService,
    SpecialtyService,
    TreatmentService,
    UrgencyService,
)
from src.config import NOT_ALLOWED

router = APIRouter(prefix="/clinic", tags=["Clinic Office"])
clinic_office_service = PatientService()
specialty_service = SpecialtyService()
plan_service = PlanService()
urgency_service = UrgencyService()


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


@router.get(
    "/patients/{patient_id}/urgencies/", response_model=Page[UrgencySerializerSchema]
)
async def get_patient_urgencies(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "patients", "action": "view"}
            )
        ),
    ],
    patient_id: int,
    urgency_filters: UrgencyFilter = FilterDepends(UrgencyFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get all urgencies for a patient"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await urgency_service.paginated_list(
        urgency_filters, page_filter, patient_id=patient_id
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/patients/urgencies/", response_model=UrgencySerializerSchema)
async def add_urgency(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {"module": "clinic_office", "model": "patients", "action": "edit"},
                    {"module": "clinic_office", "model": "urgencies", "action": "add"},
                ]
            )
        ),
    ],
    urgency: NewUpdateUrgencySchema,
):
    """Add an urgency to a patient"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await urgency_service.add(
        urgency.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)


@router.patch(
    "/patients/urgencies/{urgency_id}/", response_model=UrgencySerializerSchema
)
async def update_urgency(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {"module": "clinic_office", "model": "patients", "action": "edit"},
                    {"module": "clinic_office", "model": "urgencies", "action": "edit"},
                ]
            )
        ),
    ],
    urgency_id: int,
    urgency: NewUpdateUrgencySchema,
):
    """Update an urgency"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await urgency_service.update(
        urgency.model_dump(by_alias=False), urgency_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/patients-select/")
async def get_patients_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {
                        "module": "clinic_office",
                        "model": "patients",
                        "action": "view",
                    },
                    {"module": "clinic_office", "model": "plans", "action": "view"},
                    {"module": "clinic_office", "model": "plans", "action": "edit"},
                    {"module": "clinic_office", "model": "plans", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get patients for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_office_service.list(
        authenticated_user=authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/specialties/")
async def get_specialties(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "specialties", "action": "view"}
            )
        ),
    ],
    specialty_filters: SpecialtyFilter = FilterDepends(SpecialtyFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get specialties"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await specialty_service.paginated_list(
        specialty_filters, page_filter
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/specialties/")
async def create_specialty(
    specialty_data: NewUpdateSpecialtySchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "specialties", "action": "add"}
            )
        ),
    ],
):
    """Create a specialty"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await specialty_service.add(
        specialty_data.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)


@router.get("/specialties/{specialty_id}/")
async def get_specialty(
    specialty_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "specialties", "action": "view"}
            )
        ),
    ],
):
    """Get a specialty"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await specialty_service.get_obj_or_404(specialty_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/specialties/{specialty_id}/")
async def update_specialty(
    specialty_id: int,
    data: NewUpdateSpecialtySchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "specialties", "action": "edit"}
            )
        ),
    ],
):
    """Update a specialty"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await specialty_service.update(
        data.model_dump(by_alias=False), specialty_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/specialties/{specialty_id}/")
async def delete_specialty(
    specialty_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "specialties", "action": "delete"}
            )
        ),
    ],
):
    """Delete a specialty"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await specialty_service.delete(specialty_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/specialties-select/")
async def get_specialties_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {
                        "module": "clinic_office",
                        "model": "specialties",
                        "action": "view",
                    },
                    {"module": "clinic_office", "model": "plans", "action": "view"},
                    {"module": "clinic_office", "model": "plans", "action": "edit"},
                    {"module": "clinic_office", "model": "plans", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get specialties for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await specialty_service.list(authenticated_user=authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/plans/")
async def get_plans(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "plans", "action": "view"}
            )
        ),
    ],
    page_filter: PlanFilter = Depends(PlanFilter),
):
    """Get plans"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await plan_service.paginated_list({}, page_filter)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/plans/")
async def create_plan(
    plan_data: NewUpdatePlanSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "plans", "action": "add"}
            )
        ),
    ],
):
    """Create a plan"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await plan_service.add(
        plan_data.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)


@router.get("/plans/{plan_id}/")
async def get_plan(
    plan_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "plans", "action": "view"}
            )
        ),
    ],
):
    """Get a plan"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await plan_service.get_obj_or_404(plan_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/plans/{plan_id}/")
async def update_plan(
    plan_id: int,
    data: NewUpdatePlanSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "plans", "action": "edit"}
            )
        ),
    ],
):
    """Update a plan"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await plan_service.update(
        data.model_dump(by_alias=False), plan_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/plans/{plan_id}/")
async def delete_plan(
    plan_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "plans", "action": "delete"}
            )
        ),
    ],
):
    """Delete a plan"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await plan_service.delete(plan_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/plans-select/")
async def get_plans_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {
                        "module": "clinic_office",
                        "model": "specialties",
                        "action": "view",
                    },
                    {"module": "clinic_office", "model": "plans", "action": "view"},
                    {"module": "clinic_office", "model": "plans", "action": "edit"},
                    {"module": "clinic_office", "model": "plans", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get plans for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await plan_service.list(authenticated_user=authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/treatments/")
async def get_treatments(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "treatments", "action": "view"}
            )
        ),
    ],
    treatment_filters: TreatmentFilter = FilterDepends(TreatmentFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get treatments"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await TreatmentService().paginated_list(
        treatment_filters, page_filter
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/treatments/")
async def create_treatment(
    treatment_data: NewUpdateTreatmentSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "treatments", "action": "add"}
            )
        ),
    ],
):
    """Create a treatment"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await TreatmentService().add(
        treatment_data.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)


@router.get("/treatments/{treatment_id}/")
async def get_treatment(
    treatment_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "treatments", "action": "view"}
            )
        ),
    ],
):
    """Get a treatment"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await TreatmentService().get_obj_or_404(treatment_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/treatments/{treatment_id}/")
async def update_treatment(
    treatment_id: int,
    data: NewUpdateTreatmentSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "treatments", "action": "edit"}
            )
        ),
    ],
):
    """Update a treatment"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await TreatmentService().update(
        data.model_dump(by_alias=False), treatment_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/treatments/{treatment_id}/")
async def delete_treatment(
    treatment_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "treatments", "action": "delete"}
            )
        ),
    ],
):
    """Delete a treatment"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await TreatmentService().delete(treatment_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/treatments-select/")
async def get_treatments_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {
                        "module": "clinic_office",
                        "model": "treatments",
                        "action": "view",
                    },
                    {"module": "clinic_office", "model": "plans", "action": "view"},
                    {"module": "clinic_office", "model": "plans", "action": "edit"},
                    {"module": "clinic_office", "model": "plans", "action": "add"},
                    {"module": "clinic_office", "model": "patients", "action": "view"},
                    {"module": "clinic_office", "model": "patients", "action": "edit"},
                    {"module": "clinic_office", "model": "patients", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get treatments for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await TreatmentService().list(authenticated_user=authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/desks/")
async def get_desks(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "desks", "action": "view"}
            )
        ),
    ],
    desk_filters: DeskFilter = FilterDepends(DeskFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get desks"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await DeskService().paginated_list(desk_filters, page_filter)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/desks/")
async def create_desk(
    desk_data: NewUpdateDeskSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "desks", "action": "add"}
            )
        ),
    ],
):
    """Create a desk"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await DeskService().add(
        desk_data.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)


@router.get("/desks/{desk_id}/")
async def get_desk(
    desk_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "desks", "action": "view"}
            )
        ),
    ],
):
    """Get a desk"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await DeskService().get_obj_or_404(desk_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/desks/{desk_id}/")
async def update_desk(
    desk_id: int,
    data: NewUpdateDeskSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "desks", "action": "edit"}
            )
        ),
    ],
):
    """Update a desk"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await DeskService().update(
        data.model_dump(by_alias=False), desk_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/desks/{desk_id}/")
async def delete_desk(
    desk_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "desks", "action": "delete"}
            )
        ),
    ],
):
    """Delete a desk"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await DeskService().delete(desk_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/desks-select/")
async def get_desks_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {
                        "module": "clinic_office",
                        "model": "desks",
                        "action": "view",
                    },
                    {"module": "clinic_office", "model": "plans", "action": "view"},
                    {"module": "clinic_office", "model": "plans", "action": "edit"},
                    {"module": "clinic_office", "model": "plans", "action": "add"},
                    {"module": "clinic_office", "model": "patients", "action": "view"},
                    {"module": "clinic_office", "model": "patients", "action": "edit"},
                    {"module": "clinic_office", "model": "patients", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get desks for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await DeskService().list(authenticated_user=authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/anamnesis/")
async def get_anamnesis_list(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "anamnesis", "action": "view"}
            )
        ),
    ],
    anamnesis_filters: AnamnesisFilter = FilterDepends(AnamnesisFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get anamnesis"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await AnamnesisService().paginated_list(
        anamnesis_filters, page_filter
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/anamnesis/")
async def create_anamnesis(
    anamnesis_data: NewUpdateAnamnesisSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "anamnesis", "action": "add"}
            )
        ),
    ],
):
    """Create anamnesis"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await AnamnesisService().add(
        anamnesis_data.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)


@router.get("/anamnesis/{anamnesis_id}/")
async def get_anamnesis(
    anamnesis_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "anamnesis", "action": "view"}
            )
        ),
    ],
):
    """Get anamnesis"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await AnamnesisService().get_obj_or_404(anamnesis_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/anamnesis/{anamnesis_id}/")
async def update_anamnesis(
    anamnesis_id: int,
    data: NewUpdateAnamnesisSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "anamnesis", "action": "edit"}
            )
        ),
    ],
):
    """Update anamnesis"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await AnamnesisService().update(
        data.model_dump(by_alias=False), anamnesis_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/anamnesis/{anamnesis_id}/")
async def delete_anamnesis(
    anamnesis_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "anamnesis", "action": "delete"}
            )
        ),
    ],
):
    """Delete anamnesis"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await AnamnesisService().delete(anamnesis_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/anamnesis-select/")
async def get_anamnesis_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {
                        "module": "clinic_office",
                        "model": "anamnesis",
                        "action": "view",
                    },
                    {"module": "clinic_office", "model": "plans", "action": "view"},
                    {"module": "clinic_office", "model": "plans", "action": "edit"},
                    {"module": "clinic_office", "model": "plans", "action": "add"},
                    {"module": "clinic_office", "model": "patients", "action": "view"},
                    {"module": "clinic_office", "model": "patients", "action": "edit"},
                    {"module": "clinic_office", "model": "patients", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get anamnesis for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await AnamnesisService().list(authenticated_user=authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/questions/")
async def get_questions(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "questions", "action": "view"}
            )
        ),
    ],
    question_filters: QuestionFilter = FilterDepends(QuestionFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get questions"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await QuestionService().paginated_list(
        question_filters, page_filter
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/questions/")
async def create_question(
    question_data: NewUpdateQuestionSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "questions", "action": "add"}
            )
        ),
    ],
):
    """Create question"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await QuestionService().add(
        question_data.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)


@router.get("/questions/{question_id}/")
async def get_question(
    question_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "questions", "action": "view"}
            )
        ),
    ],
):
    """Get question"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await QuestionService().get_obj_or_404(question_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/questions/{question_id}/")
async def update_question(
    question_id: int,
    data: NewUpdateQuestionSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "questions", "action": "edit"}
            )
        ),
    ],
):
    """Update question"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await QuestionService().update(
        data.model_dump(by_alias=False), question_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/questions/{question_id}/")
async def delete_question(
    question_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "questions", "action": "delete"}
            )
        ),
    ],
):
    """Delete question"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await QuestionService().delete(question_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/questions-select/")
async def get_questions_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {
                        "module": "clinic_office",
                        "model": "questions",
                        "action": "view",
                    },
                    {"module": "clinic_office", "model": "plans", "action": "view"},
                    {"module": "clinic_office", "model": "plans", "action": "edit"},
                    {"module": "clinic_office", "model": "plans", "action": "add"},
                    {"module": "clinic_office", "model": "patients", "action": "view"},
                    {"module": "clinic_office", "model": "patients", "action": "edit"},
                    {"module": "clinic_office", "model": "patients", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get questions for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await QuestionService().list(authenticated_user=authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/documents/")
async def create_document(
    document_data: NewUpdateDocumentSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "documents", "action": "add"}
            )
        ),
    ],
):
    """Create document"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await DocumentService().add(
        document_data.model_dump(by_alias=False), authenticated_user
    )
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/documents/{document_id}/")
async def get_document(
    document_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "documents", "action": "view"}
            )
        ),
    ],
):
    """Get document"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await DocumentService().get_obj_or_404(document_id)
    path = os.path.join(response_data["file_path"], response_data["file_name"])
    headers = {"Access-Control-Expose-Headers": "Content-Disposition"}
    return FileResponse(path=path, filename=response_data["file_name"], headers=headers)


@router.patch("/documents/{document_id}/")
async def update_document(
    document_id: int,
    data: NewUpdateDocumentSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "documents", "action": "edit"}
            )
        ),
    ],
):
    """Update document"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await DocumentService().update(
        data.model_dump(by_alias=False), document_id, authenticated_user
    )
    return Response(status_code=status.HTTP_200_OK)


@router.delete("/documents/{document_id}/")
async def delete_document(
    document_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "clinic_office", "model": "documents", "action": "delete"}
            )
        ),
    ],
):
    """Delete document"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await DocumentService().delete(document_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

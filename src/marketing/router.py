"""Marketing router"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from plus_db_agent.filters import PaginationFilter
from plus_db_agent.models import UserModel

from src.backends import PermissionChecker
from src.config import NOT_ALLOWED
from src.marketing.filters import ProspectionFilter, ProspectionStageFilter
from src.marketing.schemas import (
    NewUpdateProspectionSchema,
    NewUpdateProspectionStageSchema,
    ProspectionSerializerSchema,
    ProspectionStageSerializerSchema,
)
from src.marketing.service import ProspectionService, ProspectionStageService

router = APIRouter(prefix="/marketing", tags=["Marketing"])
prospection_service = ProspectionService()
prospection_stage_service = ProspectionStageService()


@router.get("/prospections/", response_model=Page[ProspectionSerializerSchema])
async def list_prospection(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection", "action": "view"}
            )
        ),
    ],
    list_filters: ProspectionFilter = FilterDepends(ProspectionFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """List all prospections"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_service.paginated_list(
        list_filters=list_filters, page_filter=page_filter
    )


@router.post("/prospections/", response_model=ProspectionSerializerSchema)
async def create_prospection(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection", "action": "add"}
            )
        ),
    ],
    prospection: NewUpdateProspectionSchema,
):
    """Create a new prospection"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_service.add(prospection, authenticated_user)


@router.get(
    "/prospections/{prospection_id}/", response_model=ProspectionSerializerSchema
)
async def retrieve_prospection(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection", "action": "view"}
            )
        ),
    ],
    prospection_id: str,
):
    """Retrieve a prospection"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_service.get_obj_or_404(prospection_id)


@router.put(
    "/prospections/{prospection_id}/", response_model=ProspectionSerializerSchema
)
async def update_prospection(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection", "action": "edit"}
            )
        ),
    ],
    prospection_id: str,
    prospection: NewUpdateProspectionSchema,
):
    """Update a prospection"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_service.update(
        prospection_id, prospection, authenticated_user
    )


@router.delete("/prospections/{prospection_id}/", response_model=Response)
async def delete_prospection(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection", "action": "delete"}
            )
        ),
    ],
    prospection_id: str,
):
    """Delete a prospection"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    await prospection_service.delete(prospection_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/prospection-stages/", response_model=Page[ProspectionStageSerializerSchema]
)
async def list_prospection_stage(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection_stage", "action": "view"}
            )
        ),
    ],
    list_filters: ProspectionStageFilter = FilterDepends(ProspectionStageFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """List all prospection stages"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_stage_service.paginated_list(
        list_filters=list_filters, page_filter=page_filter
    )


@router.post("/prospection-stages/", response_model=ProspectionStageSerializerSchema)
async def create_prospection_stage(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection_stage", "action": "add"}
            )
        ),
    ],
    prospection_stage: NewUpdateProspectionStageSchema,
):
    """Create a new prospection stage"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_stage_service.add(prospection_stage, authenticated_user)


@router.get(
    "/prospection-stages/{prospection_stage_id}/",
    response_model=ProspectionStageSerializerSchema,
)
async def retrieve_prospection_stage(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection_stage", "action": "view"}
            )
        ),
    ],
    prospection_stage_id: str,
):
    """Retrieve a prospection stage"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_stage_service.get_obj_or_404(prospection_stage_id)


@router.put(
    "/prospection-stages/{prospection_stage_id}/",
    response_model=ProspectionStageSerializerSchema,
)
async def update_prospection_stage(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "marketing", "model": "prospection_stage", "action": "edit"}
            )
        ),
    ],
    prospection_stage_id: str,
    prospection_stage: NewUpdateProspectionStageSchema,
):
    """Update a prospection stage"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_stage_service.update(
        prospection_stage_id, prospection_stage, authenticated_user
    )


@router.delete("/prospection-stages/{prospection_stage_id}/", response_model=Response)
async def delete_prospection_stage(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {
                    "module": "marketing",
                    "model": "prospection_stage",
                    "action": "delete",
                }
            )
        ),
    ],
    prospection_stage_id: str,
):
    """Delete a prospection stage"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    await prospection_stage_service.delete(prospection_stage_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/prospection-stages/select/", response_model=List[ProspectionStageSerializerSchema]
)
async def list_prospection_stage_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {
                        "module": "marketing",
                        "model": "prospection_stage",
                        "action": "view",
                    },
                    {"module": "marketing", "model": "prospection", "action": "add"},
                    {"module": "marketing", "model": "prospection", "action": "edit"},
                    {"module": "marketing", "model": "prospection", "action": "view"},
                ]
            )
        ),
    ],
):
    """List all prospection stages for select"""
    if not authenticated_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": NOT_ALLOWED}
        )
    return await prospection_stage_service.list(clinic=authenticated_user.clinic)

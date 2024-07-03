"""Auth router"""

from typing import Annotated

from fastapi import APIRouter, Depends, Security, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.security import APIKeyHeader
from fastapi_filter import FilterDepends
from plus_db_agent.filters import PaginationFilter
from plus_db_agent.models import UserModel

from src.backends import PermissionChecker
from src.config import NOT_ALLOWED, SCHEDULER_API_KEY
from src.manager.filters import ClinicFilter, ProfileFilter, UserFilter
from src.manager.schemas import NewUpdateProfileSchema, NewUserSchema
from src.manager.service import ClinicService, ProfileService, UserService

router = APIRouter(prefix="/manager", tags=["Manager"])
user_service = UserService()
profile_service = ProfileService()
clinic_service = ClinicService()
api_key_header = APIKeyHeader(name="X-API-Key")


@router.post("/users/register/")
async def register(
    register_schema: NewUserSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "manager", "model": "users", "action": "add"})
        ),
    ],
):
    """Register a user"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await user_service.add(
        register_schema.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/users/{user_id}/")
async def get_user(
    user_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "manager", "model": "users", "action": "view"})
        ),
    ],
):
    """Get a user"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await user_service.get_obj_or_404(user_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/users/{user_id}/")
async def update_user(
    user_id: int,
    new_data: NewUserSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "manager", "model": "users", "action": "edit"})
        ),
    ],
):
    """Update a user"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await user_service.update(
        new_data.model_dump(by_alias=False), user_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/users/{user_id}/")
async def delete_user(
    user_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "users", "action": "delete"}
            )
        ),
    ],
):
    """Delete a user"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await user_service.delete(user_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users/")
async def get_users(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "manager", "model": "users", "action": "view"})
        ),
    ],
    user_filters: UserFilter = FilterDepends(UserFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get users"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await user_service.paginated_list(user_filters, page_filter)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/me/")
async def update_me(
    authenticated_user: Annotated[UserModel, Depends(PermissionChecker([], me=True))],
    new_data: NewUserSchema = Depends(),
):
    """Update self user data"""
    response_data = await user_service.update(
        new_data.model_dump(by_alias=False), authenticated_user.id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/me/")
async def get_me(
    authenticated_user: Annotated[UserModel, Depends(PermissionChecker([], me=True))],
):
    """Get self user data"""
    response_data = await user_service.get_obj_or_404(authenticated_user.id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/profiles/")
async def get_profiles(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "profiles", "action": "view"}
            )
        ),
    ],
    profile_filters: ProfileFilter = FilterDepends(ProfileFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get profiles"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await profile_service.paginated_list(profile_filters, page_filter)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/profiles/")
async def create_profile(
    profile_data: NewUpdateProfileSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "profiles", "action": "add"}
            )
        ),
    ],
):
    """Create a profile"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await profile_service.add(
        profile_data.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/profiles/{profile_id}/")
async def get_profile(
    profile_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "profiles", "action": "view"}
            )
        ),
    ],
):
    """Get a profile"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await profile_service.get_obj_or_404(profile_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/profiles/{profile_id}/")
async def update_profile(
    profile_id: int,
    data: NewUpdateProfileSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "profiles", "action": "edit"}
            )
        ),
    ],
):
    """Update a profile"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await profile_service.update(
        data.model_dump(by_alias=False), profile_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/profiles/{profile_id}/")
async def delete_profile(
    profile_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "profiles", "action": "delete"}
            )
        ),
    ],
):
    """Delete a profile"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await profile_service.delete(profile_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/profiles-select/")
async def get_profiles_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {"module": "manager", "model": "profiles", "action": "view"},
                    {"module": "manager", "model": "users", "action": "view"},
                    {"module": "manager", "model": "users", "action": "edit"},
                    {"module": "manager", "model": "users", "action": "add"},
                    {"module": "manager", "model": "clinics", "action": "view"},
                    {"module": "manager", "model": "clinics", "action": "edit"},
                    {"module": "manager", "model": "clinics", "action": "add"},
                ]
            )
        ),
    ],
):
    """Get profiles for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await profile_service.list(authenticated_user=authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/clinics/")
async def get_clinics(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "clinics", "action": "view"}
            )
        ),
    ],
    clinic_filters: ClinicFilter = FilterDepends(ClinicFilter),
    page_filter: PaginationFilter = Depends(PaginationFilter),
):
    """Get clinics"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_service.paginated_list(clinic_filters, page_filter)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/clinics/")
async def create_clinic(
    clinic_data: NewUpdateProfileSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "clinics", "action": "add"}
            )
        ),
    ],
):
    """Create a clinic"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_service.add(
        clinic_data.model_dump(by_alias=False), authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/clinics/{clinic_id}/")
async def get_clinic(
    clinic_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "clinics", "action": "view"}
            )
        ),
    ],
):
    """Get a clinic"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_service.get_obj_or_404(clinic_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/clinics/{clinic_id}/check/")
async def get_clinic_check(clinic_id: int, key_header=Security(api_key_header)):
    """Check if a clinic exists"""
    if key_header == SCHEDULER_API_KEY:
        await clinic_service.get_by_field("id", str(clinic_id))
        return JSONResponse({"message": "Clinic exists"})
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key"
    )


@router.patch("/clinics/{clinic_id}/")
async def update_clinic(
    clinic_id: int,
    data: NewUpdateProfileSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "clinics", "action": "edit"}
            )
        ),
    ],
):
    """Update a clinic"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_service.update(
        data.model_dump(by_alias=False), clinic_id, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/clinics/{clinic_id}/")
async def delete_clinic(
    clinic_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "manager", "model": "clinics", "action": "delete"}
            )
        ),
    ],
):
    """Delete a clinic"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await clinic_service.delete(clinic_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/clinics-select/")
async def get_clinics_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {"module": "manager", "model": "clinics", "action": "view"},
                    {"module": "manager", "model": "users", "action": "view"},
                    {"module": "manager", "model": "users", "action": "edit"},
                    {"module": "manager", "model": "users", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get clinics for select"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_service.list(authenticated_user=authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)

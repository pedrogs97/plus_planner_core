"""Auth router"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm as LoginSchema
from fastapi_filter import FilterDepends
from starlette.requests import Request

from src.auth.filters import UserFilter, ProfileFilter, ClinicFilter
from src.auth.models import UserModel
from src.auth.schemas import NewUserSchema, NewUpdateProfileSchema
from src.auth.service import UserService, ProfileService, ClinicService
from src.backends import PermissionChecker
from src.config import (
    MAX_PAGINATION_NUMBER,
    NOT_ALLOWED,
    PAGE_NUMBER_DESCRIPTION,
    PAGE_SIZE_DESCRIPTION,
    PAGINATION_NUMBER,
)

router = APIRouter(prefix="/auth", tags=["Auth"])
user_service = UserService()
profile_service = ProfileService()
clinic_service = ClinicService()


@router.post("/login/")
async def login(
    request: Request,
    login_schema: LoginSchema = Depends(),
):
    """Login a user"""
    response_data = await user_service.login(
        login_schema.username, login_schema.password, request.state.clinic
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/refresh-token/")
async def refresh_token(
    request: Request, token: Annotated[str, Depends(user_service.oauth2_scheme)]
):
    """Refresh a token"""
    response_data = await user_service.refresh_token(token, request.state.clinic)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/logout/")
async def logout(
    request: Request, token: Annotated[str, Depends(user_service.oauth2_scheme)]
):
    """Logout a user"""
    await user_service.logout(token, request.state.clinic)
    return JSONResponse(content={}, status_code=status.HTTP_200_OK)


@router.post("/register/")
async def register(
    register_schema: NewUserSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "users", "action": "add"})
        ),
    ],
):
    """Register a user"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await user_service.create_user(register_schema, authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/{user_id}/")
async def get_user(
    user_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "users", "action": "view"})
        ),
    ],
):
    """Get a user"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await user_service.get_user(user_id)
    return JSONResponse(
        content=response_data.model_dump(), status_code=status.HTTP_200_OK
    )


@router.patch("/{user_id}/")
async def update_user(
    user_id: int,
    new_data: NewUserSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "users", "action": "edit"})
        ),
    ],
):
    """Update a user"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await user_service.update_user(
        user_id, new_data, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.delete("/{user_id}/")
async def delete_user(
    user_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "users", "action": "delete"})
        ),
    ],
):
    """Delete a user"""
    await user_service.delete_user(user_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/")
async def get_users(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "users", "action": "view"})
        ),
    ],
    user_filters: UserFilter = FilterDepends(UserFilter),
    page: int = Query(1, ge=1, description=PAGE_NUMBER_DESCRIPTION),
    size: int = Query(
        PAGINATION_NUMBER,
        ge=1,
        le=MAX_PAGINATION_NUMBER,
        description=PAGE_SIZE_DESCRIPTION,
    ),
):
    """Get users"""
    response_data = await user_service.get_users(
        authenticated_user, user_filters, page, size
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.patch("/me/")
async def update_me(
    authenticated_user: Annotated[UserModel, Depends(PermissionChecker([], me=True))],
    new_data: NewUserSchema = Depends(),
):
    """Update self user data"""
    response_data = await user_service.update_user(
        authenticated_user.id, new_data, authenticated_user
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/me/")
async def get_me(
    authenticated_user: Annotated[UserModel, Depends(PermissionChecker([], me=True))],
):
    """Get self user data"""
    response_data = await user_service.get_user(authenticated_user.id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/profiles/")
async def get_profiles(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "profiles", "action": "view"})
        ),
    ],
    profile_filters: ProfileFilter = FilterDepends(ProfileFilter),
    page: int = Query(1, ge=1, description=PAGE_NUMBER_DESCRIPTION),
    size: int = Query(
        PAGINATION_NUMBER,
        ge=1,
        le=MAX_PAGINATION_NUMBER,
        description=PAGE_SIZE_DESCRIPTION,
    ),
):
    """Get profiles"""
    response_data = await profile_service.get_profiles(
        authenticated_user, profile_filters, page, size
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/profiles/")
async def create_profile(
    profile_data: NewUpdateProfileSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "profiles", "action": "add"})
        ),
    ],
):
    """Create a profile"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await profile_service.create_profile(
        profile_data, authenticated_user
    )
    return JSONResponse(
        content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
    )


@router.get("/profiles/{profile_id}/")
async def get_profile(
    profile_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "profiles", "action": "view"})
        ),
    ],
):
    """Get a profile"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await profile_service.get_profile(profile_id)
    return JSONResponse(
        content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
    )


@router.patch("/profiles/{profile_id}/")
async def update_profile(
    profile_id: int,
    data: NewUpdateProfileSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "profiles", "action": "edit"})
        ),
    ],
):
    """Update a profile"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await profile_service.update_profile(
        profile_id, data, authenticated_user
    )
    return JSONResponse(
        content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
    )


@router.delete("/profiles/{profile_id}/")
async def delete_profile(
    profile_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "auth", "model": "profiles", "action": "delete"}
            )
        ),
    ],
):
    """Delete a profile"""
    await profile_service.delete_profile(profile_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/profiles-select/")
async def get_profiles_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {"module": "auth", "model": "profiles", "action": "view"},
                    {"module": "auth", "model": "users", "action": "view"},
                    {"module": "auth", "model": "users", "action": "edit"},
                    {"module": "auth", "model": "users", "action": "add"},
                    {"module": "auth", "model": "clinics", "action": "view"},
                    {"module": "auth", "model": "clinics", "action": "edit"},
                    {"module": "auth", "model": "clinics", "action": "add"},
                ]
            )
        ),
    ],
):
    """Get profiles for select"""
    response_data = await profile_service.get_profiles_select(authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.get("/clinics/")
async def get_clinics(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "clinics", "action": "view"})
        ),
    ],
    clinic_filters: ClinicFilter = FilterDepends(ClinicFilter),
    page: int = Query(1, ge=1, description=PAGE_NUMBER_DESCRIPTION),
    size: int = Query(
        PAGINATION_NUMBER,
        ge=1,
        le=MAX_PAGINATION_NUMBER,
        description=PAGE_SIZE_DESCRIPTION,
    ),
):
    """Get clinics"""
    response_data = await clinic_service.get_clinics(
        authenticated_user, clinic_filters, page, size
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/clinics/")
async def create_clinic(
    clinic_data: NewUpdateProfileSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "clinics", "action": "add"})
        ),
    ],
):
    """Create a clinic"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_service.create_clinic(clinic_data, authenticated_user)
    return JSONResponse(
        content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
    )


@router.get("/clinics/{clinic_id}/")
async def get_clinic(
    clinic_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "clinics", "action": "view"})
        ),
    ],
):
    """Get a clinic"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_service.get_clinic(clinic_id)
    return JSONResponse(
        content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
    )


@router.patch("/clinics/{clinic_id}/")
async def update_clinic(
    clinic_id: int,
    data: NewUpdateProfileSchema,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "auth", "model": "clinics", "action": "edit"})
        ),
    ],
):
    """Update a clinic"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await clinic_service.update_clinic(
        clinic_id, data, authenticated_user
    )
    return JSONResponse(
        content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
    )


@router.delete("/clinics/{clinic_id}/")
async def delete_clinic(
    clinic_id: int,
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                {"module": "auth", "model": "clinics", "action": "delete"}
            )
        ),
    ],
):
    """Delete a clinic"""
    await clinic_service.delete_clinic(clinic_id, authenticated_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/clinics-select/")
async def get_clinics_select(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker(
                [
                    {"module": "auth", "model": "clinics", "action": "view"},
                    {"module": "auth", "model": "users", "action": "view"},
                    {"module": "auth", "model": "users", "action": "edit"},
                    {"module": "auth", "model": "users", "action": "add"},
                ]
            ),
        ),
    ],
):
    """Get clinics for select"""
    response_data = await clinic_service.get_clinics_select(authenticated_user)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)

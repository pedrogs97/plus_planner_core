"""Auth router"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import APIKeyHeader
from fastapi.security.oauth2 import OAuth2PasswordRequestForm as LoginSchema
from fastapi_filter import FilterDepends
from plus_db_agent.filters import PaginationFilter
from plus_db_agent.models import UserModel
from starlette.requests import Request

from src.auth.filters import UserFilter
from src.auth.schemas import NewUserSchema
from src.auth.service import UserService
from src.auth.services_old import ClinicService, ProfileService
from src.auth.services_old import UserService as UserServiceOld
from src.backends import PermissionChecker
from src.config import NOT_ALLOWED

router = APIRouter(prefix="/auth", tags=["Auth"])
user_service = UserService()
user_service_old = UserServiceOld()
profile_service = ProfileService()
clinic_service = ClinicService()
api_key_header = APIKeyHeader(name="X-API-Key")


@router.post("/login/")
async def login(
    request: Request,
    login_schema: LoginSchema = Depends(),
):
    """Login a user"""
    response_data = await user_service_old.login(
        login_schema.username, login_schema.password, request.state.clinic
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


# @router.post("/refresh-token/")
# async def refresh_token(
#     request: Request, token: Annotated[str, Depends(user_service.oauth2_scheme)]
# ):
#     """Refresh a token"""
#     response_data = await user_service.refresh_token(token, request.state.clinic)
#     return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


# @router.post("/check-token/")
# async def check_token(
#     token: Annotated[str, Depends(user_service.oauth2_scheme)],
#     key_header=Security(api_key_header),
# ):
#     """Check a token"""
#     if key_header == SCHEDULER_API_KEY and user_service.token_is_valid(token):
#         return JSONResponse({"message": "Valid token"})
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key"
#     )


# @router.post("/logout/")
# async def logout(
#     request: Request, token: Annotated[str, Depends(user_service.oauth2_scheme)]
# ):
#     """Logout a user"""
#     await user_service.logout(token, request.state.clinic)
#     return JSONResponse(content={}, status_code=status.HTTP_200_OK)


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
    response_data = await user_service.add(
        register_schema.model_dump(by_alias=False), authenticated_user
    )
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
    response_data = await user_service.get_obj_or_404(user_id)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


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
    response_data = await user_service.update(
        new_data.model_dump(by_alias=False), user_id, authenticated_user
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
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    await user_service.delete(user_id, authenticated_user)
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


# @router.get("/profiles/")
# async def get_profiles(
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker({"module": "auth", "model": "profiles", "action": "view"})
#         ),
#     ],
#     profile_filters: ProfileFilter = FilterDepends(ProfileFilter),
#     page: int = Query(1, ge=1, description=PAGE_NUMBER_DESCRIPTION),
#     size: int = Query(
#         PAGINATION_NUMBER,
#         ge=1,
#         le=MAX_PAGINATION_NUMBER,
#         description=PAGE_SIZE_DESCRIPTION,
#     ),
# ):
#     """Get profiles"""
#     response_data = await profile_service.get_profiles(
#         authenticated_user, profile_filters, page, size
#     )
#     return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


# @router.post("/profiles/")
# async def create_profile(
#     profile_data: NewUpdateProfileSchema,
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker({"module": "auth", "model": "profiles", "action": "add"})
#         ),
#     ],
# ):
#     """Create a profile"""
#     if not authenticated_user:
#         return JSONResponse(
#             content={"message": NOT_ALLOWED},
#             status_code=status.HTTP_403_FORBIDDEN,
#         )
#     response_data = await profile_service.create_profile(
#         profile_data, authenticated_user
#     )
#     return JSONResponse(
#         content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
#     )


# @router.get("/profiles/{profile_id}/")
# async def get_profile(
#     profile_id: int,
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker({"module": "auth", "model": "profiles", "action": "view"})
#         ),
#     ],
# ):
#     """Get a profile"""
#     if not authenticated_user:
#         return JSONResponse(
#             content={"message": NOT_ALLOWED},
#             status_code=status.HTTP_403_FORBIDDEN,
#         )
#     response_data = await profile_service.get_profile(profile_id)
#     return JSONResponse(
#         content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
#     )


# @router.patch("/profiles/{profile_id}/")
# async def update_profile(
#     profile_id: int,
#     data: NewUpdateProfileSchema,
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker({"module": "auth", "model": "profiles", "action": "edit"})
#         ),
#     ],
# ):
#     """Update a profile"""
#     if not authenticated_user:
#         return JSONResponse(
#             content={"message": NOT_ALLOWED},
#             status_code=status.HTTP_403_FORBIDDEN,
#         )
#     response_data = await profile_service.update_profile(
#         profile_id, data, authenticated_user
#     )
#     return JSONResponse(
#         content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
#     )


# @router.delete("/profiles/{profile_id}/")
# async def delete_profile(
#     profile_id: int,
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker(
#                 {"module": "auth", "model": "profiles", "action": "delete"}
#             )
#         ),
#     ],
# ):
#     """Delete a profile"""
#     await profile_service.delete_profile(profile_id, authenticated_user)
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


# @router.get("/profiles-select/")
# async def get_profiles_select(
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker(
#                 [
#                     {"module": "auth", "model": "profiles", "action": "view"},
#                     {"module": "auth", "model": "users", "action": "view"},
#                     {"module": "auth", "model": "users", "action": "edit"},
#                     {"module": "auth", "model": "users", "action": "add"},
#                     {"module": "auth", "model": "clinics", "action": "view"},
#                     {"module": "auth", "model": "clinics", "action": "edit"},
#                     {"module": "auth", "model": "clinics", "action": "add"},
#                 ]
#             )
#         ),
#     ],
# ):
#     """Get profiles for select"""
#     response_data = await profile_service.get_profiles_select(authenticated_user)
#     return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


# @router.get("/clinics/")
# async def get_clinics(
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker({"module": "auth", "model": "clinics", "action": "view"})
#         ),
#     ],
#     clinic_filters: ClinicFilter = FilterDepends(ClinicFilter),
#     page: int = Query(1, ge=1, description=PAGE_NUMBER_DESCRIPTION),
#     size: int = Query(
#         PAGINATION_NUMBER,
#         ge=1,
#         le=MAX_PAGINATION_NUMBER,
#         description=PAGE_SIZE_DESCRIPTION,
#     ),
# ):
#     """Get clinics"""
#     response_data = await clinic_service.get_clinics(
#         authenticated_user, clinic_filters, page, size
#     )
#     return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


# @router.post("/clinics/")
# async def create_clinic(
#     clinic_data: NewUpdateProfileSchema,
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker({"module": "auth", "model": "clinics", "action": "add"})
#         ),
#     ],
# ):
#     """Create a clinic"""
#     if not authenticated_user:
#         return JSONResponse(
#             content={"message": NOT_ALLOWED},
#             status_code=status.HTTP_403_FORBIDDEN,
#         )
#     response_data = await clinic_service.create_clinic(clinic_data, authenticated_user)
#     return JSONResponse(
#         content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
#     )


# @router.get("/clinics/{clinic_id}/")
# async def get_clinic(
#     clinic_id: int,
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker({"module": "auth", "model": "clinics", "action": "view"})
#         ),
#     ],
# ):
#     """Get a clinic"""
#     if not authenticated_user:
#         return JSONResponse(
#             content={"message": NOT_ALLOWED},
#             status_code=status.HTTP_403_FORBIDDEN,
#         )
#     response_data = await clinic_service.get_clinic(clinic_id)
#     return JSONResponse(
#         content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
#     )


# @router.get("/clinics/{clinic_id}/check/")
# async def get_clinic_check(clinic_id: int, key_header=Security(api_key_header)):
#     """Check if a clinic exists"""
#     if key_header == SCHEDULER_API_KEY:
#         await clinic_service.get_clinic(clinic_id)
#         return JSONResponse({"message": "Clinic exists"})
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key"
#     )


# @router.patch("/clinics/{clinic_id}/")
# async def update_clinic(
#     clinic_id: int,
#     data: NewUpdateProfileSchema,
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker({"module": "auth", "model": "clinics", "action": "edit"})
#         ),
#     ],
# ):
#     """Update a clinic"""
#     if not authenticated_user:
#         return JSONResponse(
#             content={"message": NOT_ALLOWED},
#             status_code=status.HTTP_403_FORBIDDEN,
#         )
#     response_data = await clinic_service.update_clinic(
#         clinic_id, data, authenticated_user
#     )
#     return JSONResponse(
#         content=response_data.model_dump(by_alias=True), status_code=status.HTTP_200_OK
#     )


# @router.delete("/clinics/{clinic_id}/")
# async def delete_clinic(
#     clinic_id: int,
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker(
#                 {"module": "auth", "model": "clinics", "action": "delete"}
#             )
#         ),
#     ],
# ):
#     """Delete a clinic"""
#     await clinic_service.delete_clinic(clinic_id, authenticated_user)
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


# @router.get("/clinics-select/")
# async def get_clinics_select(
#     authenticated_user: Annotated[
#         UserModel,
#         Depends(
#             PermissionChecker(
#                 [
#                     {"module": "auth", "model": "clinics", "action": "view"},
#                     {"module": "auth", "model": "users", "action": "view"},
#                     {"module": "auth", "model": "users", "action": "edit"},
#                     {"module": "auth", "model": "users", "action": "add"},
#                 ]
#             ),
#         ),
#     ],
# ):
#     """Get clinics for select"""
#     response_data = await clinic_service.get_clinics_select(authenticated_user)
#     return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)

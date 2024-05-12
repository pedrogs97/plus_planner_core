"""Auth router"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm as LoginSchema
from fastapi_filter import FilterDepends
from starlette.requests import Request

from src.auth.filters import UserFilter
from src.auth.models import UserModel
from src.auth.schemas import NewUserSchema
from src.auth.service import UserService
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

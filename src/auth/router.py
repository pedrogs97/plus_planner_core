"""Auth router"""

from typing import Annotated, Union

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm as LoginSchema

from src.auth.models import UserModel
from src.auth.schemas import NewUserSchema
from src.auth.service import UserService
from src.backends import PermissionChecker
from src.config import NOT_ALLOWED

router = APIRouter(prefix="/auth", tags=["Auth"])
user_service = UserService()


@router.post("/login/")
async def login(
    login_schema: LoginSchema = Depends(),
):
    """Login a user"""
    response_data = await user_service.login(
        login_schema.username, login_schema.password
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/refresh-token/")
async def refresh_token(token: Annotated[str, Depends(user_service.oauth2_scheme)]):
    """Refresh a token"""
    response_data = await user_service.refresh_token(token)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/logout/")
async def logout(token: Annotated[str, Depends(user_service.oauth2_scheme)]):
    """Logout a user"""
    await user_service.logout(token)
    return JSONResponse(content={}, status_code=status.HTTP_200_OK)


@router.post("/register/")
async def register(
    register_schema: NewUserSchema,
    authenticated_user: Union[UserModel, None] = Depends(
        PermissionChecker({"module": "lending", "model": "lending", "action": "add"})
    ),
):
    """Register a user"""
    if not authenticated_user:
        return JSONResponse(
            content={"message": NOT_ALLOWED},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    response_data = await user_service.create_user(register_schema)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)

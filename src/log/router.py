"""Log routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from plus_db_agent.models import LogModel, UserModel
from tortoise.expressions import Q

from src.backends import PermissionChecker
from src.config import (
    DEFAULT_DATE_TIME_FORMAT,
    MAX_PAGINATION_NUMBER,
    NOT_ALLOWED,
    PAGE_NUMBER_DESCRIPTION,
    PAGE_SIZE_DESCRIPTION,
    PAGINATION_NUMBER,
)
from src.log.schemas import LogSerializerSchema

log_router = APIRouter(prefix="/logs", tags=["Log"])


@log_router.get("/")
def get_list_logs_route(
    authenticated_user: Annotated[
        UserModel,
        Depends(
            PermissionChecker({"module": "logs", "model": "log", "action": "view"})
        ),
    ],
    search: str = "",
    page: int = Query(1, ge=1, description=PAGE_NUMBER_DESCRIPTION),
    size: int = Query(
        PAGINATION_NUMBER,
        ge=1,
        le=MAX_PAGINATION_NUMBER,
        description=PAGE_SIZE_DESCRIPTION,
    ),
):
    """List logs and apply filters route"""
    if not authenticated_user.is_clinic_master:
        return JSONResponse(
            content={"message": NOT_ALLOWED}, status_code=status.HTTP_403_FORBIDDEN
        )

    if search != "":
        log_list = (
            LogModel.filter(
                Q(
                    module__icontains=search,
                    model__icontains=search,
                    operation__icontains=search,
                    identifier__icontains=search,
                )
            )
            .prefetch_related("user")
            .filter(Q(user__username__icontains=search), user__is_active=True)
        )
    else:
        log_list = LogModel.all().prefetch_related("user")

    params = Params(page=page, size=size)
    paginated = paginate(
        log_list.order_by("-logged_in"),
        params=params,
        transformer=lambda log_list: [
            LogSerializerSchema(
                id=log.id,
                identifier=log.identifier,
                module=log.module,
                model=log.model,
                operation=log.operation,
                logged_in=log.logged_in.strftime(DEFAULT_DATE_TIME_FORMAT),
                user={
                    "id": log.user.id,
                    "fullName": log.user.full_name,
                },
            )
            for log in log_list
        ],
    )
    return paginated

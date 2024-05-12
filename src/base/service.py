""" """
from typing import Type

from fastapi import status
from fastapi.exceptions import HTTPException
from typing_extensions import Self


class BaseService:
    """"""

    model: Type

    _instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls._instance:
            cls._instance = super(BaseService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    async def get_obj_or_404(self, obj_id: int):
        """"""
        obj = await self.model.get_or_none(obj_id)
        if not obj:
            raise HTTPException(
                detail={"field": "id", "message": "Usuário não encontrado"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return obj

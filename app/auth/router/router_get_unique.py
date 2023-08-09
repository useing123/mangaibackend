from typing import Any, Optional

from fastapi import Depends
from pydantic import Field

from app.utils import AppModel

from ..adapters.jwt_service import JWTData
from ..service import Service, get_service
from . import router


@router.get("/users/count", response_model=int)
def get_users_count(svc: Service = Depends(get_service)) -> int:
    return svc.repository.count_users()

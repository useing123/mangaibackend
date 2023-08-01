from fastapi import Depends, HTTPException, status
from typing import Optional
from app.utils import AppModel
from ..service import Service, get_service
from ..adapters.jwt_service import JWTData
from . import router
from .dependencies import parse_jwt_user_data
from typing import List, Optional

class UpdateUserRequest(AppModel):
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    favorite_genres: Optional[List[str]]
    read_mangas: Optional[List[str]]

@router.put("/users/me")
async def update_user(
    update_data: UpdateUserRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    user_id = jwt_data.user_id
    user = svc.repository.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    update_dict = update_data.dict(exclude_unset=True)

    if update_dict:
        svc.repository.update_user(user_id, update_dict)

    return {"detail": "User data updated successfully."}


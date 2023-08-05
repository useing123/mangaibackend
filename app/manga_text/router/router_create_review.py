from fastapi import Depends, status

from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel
from ..service import Service, get_service
from ..adapters.jwt_service import JWTData
from datetime import datetime
from . import router

from pydantic import Field

from fastapi import HTTPException

class Review(AppModel):
    user_id: str
    review: str
    rating: int
    created_at: datetime


class ReviewCreateRequest(AppModel):
    manga_id: str
    review: str
    rating: int = Field(..., ge=0, le=10)


@router.post("/reviews", status_code=status.HTTP_201_CREATED)
def create_review(
    input: ReviewCreateRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),  # This line ensures the user is authenticated
    svc: Service = Depends(get_service),
):
    result = svc.repository.create_review(input.dict(), input.manga_id, jwt_data.user_id)
    return {"review_id": str(result.inserted_id)}






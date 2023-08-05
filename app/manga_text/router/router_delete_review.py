from fastapi import Depends, status

from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel
from ..service import Service, get_service
from ..adapters.jwt_service import JWTData
from datetime import datetime
from . import router

from fastapi import HTTPException

class Review(AppModel):
    user_id: str
    review: str
    rating: int
    created_at: datetime


@router.delete("/reviews/{review_id}")
def delete_review(
    review_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    existing_review = svc.repository.get_review_by_id(review_id)
    if not existing_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if existing_review["user_id"] != jwt_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this review")

    result = svc.repository.delete_review(review_id, jwt_data.user_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    return {"message": "Review deleted"}
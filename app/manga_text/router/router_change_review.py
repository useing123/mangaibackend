from fastapi import Depends, status, HTTPException
from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel
from ..service import Service, get_service
from ..adapters.jwt_service import JWTData
from datetime import datetime
from . import router


class Review(AppModel):
    user_id: str
    review: str
    rating: int
    created_at: datetime

class ReviewUpdateRequest(AppModel):
    review: str
    rating: int


@router.put("/reviews/{review_id}", status_code=status.HTTP_200_OK)
def update_review(
    review_id: str,
    input: ReviewUpdateRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    existing_review = svc.repository.get_review_by_id(review_id)
    if not existing_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if existing_review["user_id"] != jwt_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this review")

    update_data = {
        "review": input.review,
        "rating": input.rating,
    }

    result = svc.repository.update_review(review_id, update_data)
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Review update failed")

    updated_review = {**existing_review, **update_data}
    return str(updated_review)
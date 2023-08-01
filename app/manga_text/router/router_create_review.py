from fastapi import Depends, status

from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel
from ..service import Service, get_service
from ..adapters.jwt_service import JWTData
from datetime import datetime
from . import router

from fastapi import HTTPException

class ReviewCreateRequest(AppModel):
    manga_id: str
    review: str
    rating: int

class Review(AppModel):
    user_id: str
    review: str
    rating: int
    created_at: datetime

class ReviewList(AppModel):
    reviews: list[Review]

@router.post("/reviews", status_code=status.HTTP_201_CREATED)
def create_review(
    input: ReviewCreateRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),  # This line ensures the user is authenticated
    svc: Service = Depends(get_service),
):
    result = svc.repository.create_review(input.dict(), input.manga_id, jwt_data.user_id)
    return {"review_id": str(result.inserted_id)}

@router.get("/reviews/{manga_id}", response_model=ReviewList)
def get_reviews(
    manga_id: str,
    svc: Service = Depends(get_service),
):
    reviews = svc.repository.get_reviews_by_manga(manga_id)
    return ReviewList(reviews=reviews)

@router.delete("/reviews/{review_id}")
def delete_review(
    review_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    result = svc.repository.delete_review(review_id, jwt_data.user_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return {"message": "Review deleted"}

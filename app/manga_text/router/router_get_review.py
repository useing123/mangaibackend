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

class ReviewList(AppModel):
    reviews: list[Review]


@router.get("/reviews/{manga_id}", response_model=ReviewList)
def get_reviews(
    manga_id: str,
    svc: Service = Depends(get_service),
):
    reviews = svc.repository.get_reviews_by_manga(manga_id)
    return ReviewList(reviews=reviews)

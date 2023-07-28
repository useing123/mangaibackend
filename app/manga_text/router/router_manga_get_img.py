from fastapi import Depends, HTTPException, status
from app.utils import AppModel
from ..service import Service, get_service
from . import router

from typing import List, Optional
from fastapi import HTTPException

class MangaDetailsResponse(AppModel):
    imgur_links: Optional[List[str]]
    manga_frames_description: Optional[List[str]]
    manga_story_dialogs: Optional[List[str]]

@router.get("/read/details/{manga_id}", response_model=MangaDetailsResponse)
def get_manga_details(
    manga_id: str,  # Add manga_id as a parameter
    svc: Service = Depends(get_service),
) -> MangaDetailsResponse:
    manga_data = svc.repository.get_manga(manga_id)

    if not manga_data:
        raise HTTPException(status_code=404, detail="Manga not found")

    manga = MangaDetailsResponse(
        imgur_links=manga_data.get("imgur_links"),
        manga_frames_description=manga_data.get("manga_frames_description"),
        manga_story_dialogs=manga_data.get("manga_story_dialogs"),
    )

    return manga

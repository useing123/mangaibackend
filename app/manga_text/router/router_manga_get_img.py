from fastapi import Depends, HTTPException, status
from app.utils import AppModel
from ..service import Service, get_service
from . import router

from typing import List

from typing import Optional

class MangaDetailsResponse(AppModel):
    imgur_links: Optional[List[str]]
    manga_frames_description: Optional[List[str]]
    manga_story_dialogs: Optional[List[str]]

@router.get("/read/details", response_model=List[MangaDetailsResponse])
def get_manga_details(
    svc: Service = Depends(get_service),
) -> List[MangaDetailsResponse]:
    mangas_data = svc.repository.get_all_mangas()

    mangas = [MangaDetailsResponse(
        imgur_links=manga.get("imgur_links"),
        manga_frames_description=manga.get("manga_frames_description"),
        manga_story_dialogs=manga.get("manga_story_dialogs"),
    ) for manga in mangas_data]

    return mangas

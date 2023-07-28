from fastapi import Depends, HTTPException, status
from app.utils import AppModel
from ..service import Service, get_service
from . import router

class MangaDetailsResponse(AppModel):
    imgur_links: str
    manga_frames_description: str
    manga_story_dialogs: str

@router.get("/read/details/{manga_id}", response_model=MangaDetailsResponse)
def get_manga_details(
    manga_id: str,
    svc: Service = Depends(get_service),
) -> MangaDetailsResponse:
    manga_data = svc.repository.get_manga(manga_id)

    if manga_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manga not found")

    imgur_links = manga_data.get("imgur_links", "")
    manga_frames_description = manga_data.get("manga_frames_description", "")
    manga_story_dialogs = manga_data.get("manga_story_dialogs", "")

    return MangaDetailsResponse(
        imgur_links=imgur_links,
        manga_frames_description=manga_frames_description,
        manga_story_dialogs=manga_story_dialogs
    )

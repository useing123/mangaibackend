from fastapi import Depends, HTTPException, status
from app.utils import AppModel
from ..service import Service, get_service
from . import router
#import depends

class MangaGetResponse(AppModel):
    manga_id: str
    genre: str
    chapters_count: int
    user_id: str
    title: str
    chapters_title: list[str]
    main_characters: str
    funservice_characters: str
    detailed_characters: str
    manga_chapters_story: str
    manga_frames_description: str
    manga_story_dialogs: str
    manga_images_description: str
    imgur_links: list[str]  # Add this line

@router.get("/read/{manga_id}", response_model=MangaGetResponse)
def get_manga(
    manga_id: str,
    svc: Service = Depends(get_service),
) -> MangaGetResponse:
    manga_data = svc.repository.get_manga(manga_id)

    if manga_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manga not found")

    manga = MangaGetResponse(
        manga_id=str(manga_data["_id"]),
        genre=manga_data["genre"],
        chapters_count=manga_data["chapters_count"],
        user_id=manga_data.get("user_id", ""),
        title=manga_data.get("title", ""),
        chapters_title=manga_data.get("chapters_title", []),
        main_characters=manga_data.get("main_characters", ""),
        funservice_characters=manga_data.get("funservice_characters", ""),
        detailed_characters=manga_data.get("detailed_characters", ""),
        manga_chapters_story=manga_data.get("manga_chapters_story", ""),
        manga_frames_description=manga_data.get("manga_frames_description", ""),
        manga_story_dialogs=manga_data.get("manga_story_dialogs", ""),
        manga_images_description=manga_data.get("manga_images_description", ""),
        imgur_links=manga_data.get("imgur_links", [])  # And add this line
    )

    return manga

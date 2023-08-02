from fastapi import Depends, BackgroundTasks, status

from app.utils import AppModel
from ..service import Service, get_service
from ..tasks.generators import fill_manga_info
from . import router


class MangaCreateRequest(AppModel):
    genre: str
    prompt: str
    chapters_count: int


class MangaCreateResponse(AppModel):
    manga_id: str


@router.post(
    "/generate", status_code=status.HTTP_201_CREATED, response_model=MangaCreateResponse
)
def create_manga(
    input: MangaCreateRequest,
    background_tasks: BackgroundTasks,
    svc: Service = Depends(get_service),
) -> MangaCreateResponse:
    result = svc.repository.create_manga(input.dict())

    manga_id = str(result.inserted_id)
    manga_genre = input.genre
    num_of_chapters = input.chapters_count
    prompt = input.prompt

    background_tasks.add_task(
        fill_manga_info,
        manga_id,
        manga_genre,
        prompt,
        num_of_chapters,
        svc.repository
    )

    return MangaCreateResponse(manga_id=manga_id)

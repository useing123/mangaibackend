from fastapi import Depends, BackgroundTasks, status

from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel
from ..service import Service, get_service
from ..adapters.jwt_service import JWTData
from ..tasks.generators import fill_manga_info
from . import router

import threading

from queue import Queue
import threading

# Create a Queue
manga_generation_queue = Queue()

def worker():
    while True:
        # Get a task from the queue
        task = manga_generation_queue.get()
        if task is None:
            # If we received a None task, it means the queue is empty and we should stop the worker
            break

        # Execute the task
        task()

        # Notify the queue that the task is done
        manga_generation_queue.task_done()

# Start the worker thread
worker_thread = threading.Thread(target=worker)
worker_thread.start()


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
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> MangaCreateResponse:
    result = svc.repository.create_manga(input.dict(), jwt_data.user_id)

    manga_id = str(result.inserted_id)
    manga_genre = input.genre
    num_of_chapters = input.chapters_count
    prompt = input.prompt

    # Add a task to the queue
    manga_generation_queue.put(lambda: fill_manga_info(manga_id, manga_genre, prompt, num_of_chapters, svc.repository))

    return MangaCreateResponse(manga_id=manga_id)


# @router.post(
#     "/generate", status_code=status.HTTP_201_CREATED, response_model=MangaCreateResponse
# )from fastapi import Depends, BackgroundTasks, status

from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel
from ..service import Service, get_service
from ..adapters.jwt_service import JWTData
from ..tasks.generators import fill_manga_info
from . import router

import threading

from queue import Queue
import threading

# Create a Queue
manga_generation_queue = Queue()

def worker():
    while True:
        # Get a task from the queue
        task = manga_generation_queue.get()
        if task is None:
            # If we received a None task, it means the queue is empty and we should stop the worker
            break

        # Execute the task
        task()

        # Notify the queue that the task is done
        manga_generation_queue.task_done()

# Start the worker thread
worker_thread = threading.Thread(target=worker)
worker_thread.start()


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
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> MangaCreateResponse:
    result = svc.repository.create_manga(input.dict(), jwt_data.user_id)

    manga_id = str(result.inserted_id)
    manga_genre = input.genre
    num_of_chapters = input.chapters_count
    prompt = input.prompt

    # Add a task to the queue
    manga_generation_queue.put(lambda: fill_manga_info(manga_id, manga_genre, prompt, num_of_chapters, svc.repository))

    return MangaCreateResponse(manga_id=manga_id)


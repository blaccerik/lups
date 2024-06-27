import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response
from pydantic import constr
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from database.postgres_database import get_postgres_db
from schemas.auth import Userv2
from schemas.music_schema import Filter, SongReaction, QueuePrevious, Song
from services.music.filter_service import read_filters_by_user, create_filters_by_user, update_filters_by_user
from services.music.queue_service import read_queue, read_previous, read_new_songs
from services.music.song_service import update_song_reaction, read_song_image, read_song_audio, \
    read_artist_image, read_song
from utils.auth import get_user_v2
from utils.celery_config import celery_app

router = APIRouter(prefix="/api/music", tags=["Music"])
logger = logging.getLogger(__name__)


@router.get("/")
async def get_music(
):
    return "get works"


@router.get("/celery-test")
async def get_music(
):
    celery_app.send_task("test", args=[1], queue="music:1")
    return "hello"


@router.get("/song/{song_id}", response_model=Song)
async def get_song(
        song_id: constr(min_length=11, max_length=11),
        postgres_client: Session = Depends(get_postgres_db)
):
    return read_song(song_id, postgres_client)


@router.post("/song/{song_id}")
async def post_song_reaction(
        song_id: constr(min_length=11, max_length=11),
        song_reaction: SongReaction,
        user: Userv2 = Depends(get_user_v2),
        postgres_client: Session = Depends(get_postgres_db)
):
    return update_song_reaction(user.user_id, song_id, song_reaction, postgres_client)


@router.get("/song/{song_id}/image", response_class=FileResponse)
async def get_song_image(
        song_id: constr(min_length=11, max_length=11)
):
    image_path, exists = read_song_image(song_id)
    response = FileResponse(image_path)
    if exists:
        response.headers["Cache-Control"] = "public, max-age=1"
    return response


@router.get("/song/{song_id}/audio", response_model=str)
async def get_song_audio(
        song_id: constr(min_length=11, max_length=11),
        response: Response
):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return read_song_audio(song_id)


@router.get("/artist/{artist_id}/image", response_class=FileResponse)
async def get_artist_image(artist_id: str):
    image_path, exists = read_artist_image(artist_id)
    response = FileResponse(image_path)
    if exists:
        response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@router.get("/filters", response_model=List[Filter])
async def get_user_filters(
        user: Userv2 = Depends(get_user_v2),
        postgres_client: Session = Depends(get_postgres_db)
):
    return read_filters_by_user(user.user_id, postgres_client)


@router.post("/filters")
async def post_user_filter(
        f: Filter,
        user: Userv2 = Depends(get_user_v2),
        postgres_client: Session = Depends(get_postgres_db)
):
    return create_filters_by_user(user.user_id, f, postgres_client)


@router.put("/filters")
async def put_user_filter(
        f: Filter,
        user: Userv2 = Depends(get_user_v2),
        postgres_client: Session = Depends(get_postgres_db)
):
    return update_filters_by_user(user.user_id, f, postgres_client)


@router.get("/queue/previous", response_model=List[QueuePrevious])
async def get_user_previous(
        user: Userv2 = Depends(get_user_v2),
        postgres_client: Session = Depends(get_postgres_db)
):
    return read_previous(user.user_id, postgres_client)


@router.get("/queue/new", response_model=List[Song])
async def get_new_songs(postgres_client: Session = Depends(get_postgres_db)):
    return read_new_songs(postgres_client)


@router.get("/queue/{song_id}", response_model=List[Song])
async def get_user_queue(
        song_id: constr(min_length=11, max_length=11),
        filter_id: Optional[int] = Query(None, description="Filter ID"),
        user: Userv2 = Depends(get_user_v2),
        postgres_client: Session = Depends(get_postgres_db)
):
    return read_queue(user.user_id, song_id, filter_id, postgres_client)

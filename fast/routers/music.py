import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import constr
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from database.postgres_database import get_postgres_db
from schemas.auth import Userv2
from schemas.music import Song, Filter, SongQueue, SongReaction
from services.music_service import read_song, read_song_image, read_artist_image, read_filters_by_user, \
    create_filters_by_user, update_filters_by_user, read_queue, update_song_reaction
from utils.auth import get_user_v2

router = APIRouter(prefix="/api/music", tags=["Music"])
logger = logging.getLogger(__name__)


@router.get("/")
async def get_music(
):
    return "get works"


@router.get("/song/{song_id}", response_model=Song)
async def get_song(song_id: str, postgres_client: Session = Depends(get_postgres_db)):
    return read_song(song_id, postgres_client)


@router.post("/song/{song_id}")
async def post_song_reaction(
        song_id: str,
        song_reaction: SongReaction,
        user: Userv2 = Depends(get_user_v2),
        postgres_client: Session = Depends(get_postgres_db)
):
    return update_song_reaction(user.user_id, song_id, song_reaction, postgres_client)


@router.get("/song/{song_id}/image", response_class=FileResponse)
async def get_song_image(song_id: str):
    image_path = read_song_image(song_id)
    return FileResponse(image_path)


@router.get("/artist/{artist_id}/image", response_class=FileResponse)
async def get_artist_image(artist_id: str):
    image_path = read_artist_image(artist_id)
    return FileResponse(image_path)


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


@router.get("/queue/{song_id}", response_model=SongQueue)
async def get_user_queue(
        song_id: constr(min_length=11, max_length=11),
        filter_id: Optional[int] = Query(None, description="Filter ID"),
        # user: Userv2 = Depends(get_user_v2),
        postgres_client: Session = Depends(get_postgres_db)
):
    return read_queue(1, song_id, filter_id, postgres_client)

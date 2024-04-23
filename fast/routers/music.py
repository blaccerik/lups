import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from database.postgres_database import get_postgres_db
from schemas.music import Song
from services.music_service import read_song, read_song_image, read_artist_image

router = APIRouter(prefix="/api/music")
logger = logging.getLogger(__name__)


@router.get("/")
async def get_music(
):
    return "get works"


@router.get("/song/{song_id}", response_model=Song)
async def get_song(song_id: str, postgres_client: Session = Depends(get_postgres_db)):
    return read_song(song_id, postgres_client)


@router.get("/song/{song_id}/image", response_class=FileResponse)
async def get_song_image(song_id: str):
    image_path = read_song_image(song_id)
    return FileResponse(image_path)


@router.get("/artist/{artist_id}/image", response_class=FileResponse)
async def get_artist_image(artist_id: str):
    image_path = read_artist_image(artist_id)
    return FileResponse(image_path)

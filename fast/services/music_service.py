import logging
import os
import platform
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from database.models import DBSong, DBArtist
from schemas.music import Song, Artist

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
operating_system = platform.system()
if operating_system == 'Windows':
    MUSIC_DATA = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/music_data"
else:
    MUSIC_DATA = "/usr/src/app/music_data"
logger.info(MUSIC_DATA)


def read_song(song_id: str, postgres_client: Session) -> Song:
    dbsa = postgres_client.query(DBSong, DBArtist).join(
        DBArtist, DBSong.artist_id == DBArtist.id
    ).filter(DBSong.id == song_id).first()
    if dbsa is None:
        raise HTTPException(status_code=404, detail="Song not found")
    dbsong, dbartist = dbsa
    artist = None
    if dbartist:
        artist = Artist(
            name=dbartist.name,
            id=dbartist.id
        )
    return Song(
        id=dbsong.id,
        title=dbsong.title,
        length=dbsong.length,
        type=dbsong.type,
        artist=artist
    )


def read_song_image(song_id: str) -> str:
    # try to find image
    path = f"{MUSIC_DATA}/song_images/{song_id}.jpg"
    if os.path.exists(path):
        return path
    raise HTTPException(status_code=404, detail="Song image not found")


def read_artist_image(artist_id: str) -> str:
    # try to find image
    path = f"{MUSIC_DATA}/artist_images/{artist_id}.jpg"
    if os.path.exists(path):
        return path
    raise HTTPException(status_code=404, detail="Artist image not found")

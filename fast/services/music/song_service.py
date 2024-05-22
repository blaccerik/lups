import logging
import os
import platform
from pathlib import Path

from fastapi import HTTPException
from pytube import YouTube
from sqlalchemy.orm import Session

from database.models import DBSong, DBArtist, DBReaction
from schemas.music import Song, Artist, SongReaction, ReactionType
from utils.celery_config import celery_app

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
operating_system = platform.system()
if operating_system == 'Windows':
    MUSIC_DATA = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/music_data"
else:
    MUSIC_DATA = "/usr/src/app/music_data"
logger.info(MUSIC_DATA)
MIN_QUEUE_SONGS = 40
DEFAULT_SONG_IMAGE_PATH = "assets/default_song_image.png"


def read_song(song_id: str, postgres_client: Session) -> Song:
    dbsa = postgres_client.query(DBSong, DBArtist).join(
        DBArtist, DBSong.artist_id == DBArtist.id
    ).filter(DBSong.id == song_id).first()
    if dbsa is None:
        celery_app.send_task("find_new_songs", args=[song_id], queue="music:1")
        raise HTTPException(status_code=404, detail="Song not found")
    dbsong, dbartist = dbsa
    artist = None
    if dbartist:
        artist = Artist(
            name=dbartist.name,
            id=dbartist.id
        )
    return Song(
        id=song_id,
        title=dbsong.title,
        length=dbsong.length,
        type=dbsong.type,
        artist=artist,
    )


def read_song_audio(song_id: str) -> str:
    yt = YouTube(f"https://www.youtube.com/watch?v={song_id}")
    best = 999999999
    link = None
    bads = [
        "avc1", "vp9"
    ]
    try:
        streams = yt.streaming_data["adaptiveFormats"]
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail="Song audio not found")
    for i in streams:
        br = i['bitrate']
        mt = i['mimeType']
        if any(bad in mt for bad in bads):
            continue
        if br < best:
            link = i['url']
            best = br
    if link is None:
        raise HTTPException(status_code=404, detail="Song audio not found")
    return link


def read_song_image(song_id: str) -> str:
    # try to find image
    path = f"{MUSIC_DATA}/song_images/{song_id}.jpg"
    if os.path.exists(path):
        return path
    return DEFAULT_SONG_IMAGE_PATH


def read_artist_image(artist_id: str) -> str:
    # try to find image
    path = f"{MUSIC_DATA}/artist_images/{artist_id}.jpg"
    if os.path.exists(path):
        return path
    raise HTTPException(status_code=404, detail="Artist image not found")


def update_song_reaction(user_id: int, song_id: str, song_reaction: SongReaction, postgres_client: Session):
    # check if user has feedback
    dbr = postgres_client.get(DBReaction, (song_id, user_id))
    if dbr is None:
        dbr = DBReaction(
            song_id=song_id,
            user_id=user_id,
            duration=song_reaction.duration,
            type=song_reaction.type
        )
    else:
        dbr.duration = dbr.duration + song_reaction.duration

    if song_reaction.type == ReactionType.like:
        dbr.type = song_reaction.type

    postgres_client.add(dbr)
    postgres_client.commit()

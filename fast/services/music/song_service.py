import logging
import os
import platform
from pathlib import Path

import requests
from fastapi import HTTPException
from pytube import YouTube
from sqlalchemy.orm import Session

from database.models import DBSong, DBArtist, DBReaction
from schemas.music_schema import Song, Artist, SongReaction, SongStatus
from utils.scrapping import start_scrape_for_song

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


def _is_song_id_valid(song_id: str):
    # hack by https://gist.github.com/tonY1883/a3b85925081688de569b779b4657439b
    url = f"https://img.youtube.com/vi/{song_id}/mqdefault.jpg"
    response = requests.head(url, allow_redirects=True, timeout=3)
    print(response.status_code == 200)
    return response == 200


def read_song(song_id: str, postgres_client: Session) -> SongStatus:
    # check database first for song
    # then check youtube api
    dbs, dba = postgres_client.query(DBSong, DBArtist).join(
        DBArtist, DBSong.artist_id == DBArtist.id
    ).filter(DBSong.id == song_id).first()
    # dbs, dba = dbsa if None
    if dbs and dbs.status == "scrapping":
        return SongStatus(type='scrapping', song=None)
    elif dbs and dbs.status == "ready":
        return SongStatus(type='ready', song=Song(
            id=song_id,
            title=dbs.title,
            length=dbs.length,
            type=dbs.type,
            artist=Artist(name=dba.name, id=dba.id) if dba else None
        ))
    elif dbs and dbs.status == "idle":
        start_scrape_for_song(song_id, postgres_client)
        return SongStatus(type='scrapping', song=None)
    elif _is_song_id_valid(song_id):
        start_scrape_for_song(song_id, postgres_client)
        return SongStatus(type='scrapping', song=None)
    else:
        raise HTTPException(status_code=404, detail="Song not found")


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
    # TODO default artist image
    raise HTTPException(status_code=404, detail="Artist image not found")


def update_song_reaction(user_id: int, song_id: str, song_reaction: SongReaction, postgres_client: Session):
    # check if user has feedback
    dbr = postgres_client.get(DBReaction, (song_id, user_id))
    if dbr is None:
        dbr = DBReaction(
            song_id=song_id,
            user_id=user_id,
            duration=song_reaction.duration,
        )
    else:
        dbr.duration = dbr.duration + song_reaction.duration
    dbr.liked = song_reaction.liked
    postgres_client.add(dbr)
    postgres_client.commit()

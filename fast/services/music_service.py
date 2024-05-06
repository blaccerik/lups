import json
import logging
import os
import platform
from pathlib import Path
from typing import List

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBSong, DBArtist, DBFilter, DBReaction, DBSongData
from schemas.music import Song, Artist, Filter, FilterConfig, SongQueue, Similarity
from utils.celery_config import celery_app
from utils.music_query import MusicQuery

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
    path = f"{MUSIC_DATA}/songs/{song_id}.mp3"
    return Song(
        id=dbsong.id,
        title=dbsong.title,
        length=dbsong.length,
        type=dbsong.type,
        artist=artist,
        has_audio=os.path.exists(path)
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


def read_filters_by_user(user_id: int, postgres_client: Session) -> List[Filter]:
    dbfs = postgres_client.query(DBFilter).filter(
        DBFilter.user_id == user_id
    ).all()

    result = []
    for dbf in dbfs:
        config_list = json.loads(dbf.config)
        f = Filter(
            id=dbf.id,
            name=dbf.name,
            config=[FilterConfig(**c) for c in config_list]
        )
        result.append(f)
    return result


def create_filters_by_user(user_id: int, f: Filter, postgres_client: Session):
    dbf = DBFilter()
    dbf.name = f.name
    dbf.user_id = user_id
    dbf.config = json.dumps([c.model_dump() for c in f.config])
    postgres_client.add(dbf)
    postgres_client.commit()


def update_filters_by_user(user_id: int, f: Filter, postgres_client: Session):
    dbf = postgres_client.query(DBFilter).filter(and_(
        DBFilter.user_id == user_id,
        DBFilter.id == f.id
    )).first()
    if dbf is None:
        raise HTTPException(status_code=404, detail="User doesn't have this filter")
    if f.delete:
        postgres_client.delete(dbf)
        postgres_client.commit()
        return
    else:
        dbf.name = f.name
        dbf.user_id = user_id
        dbf.config = json.dumps([c.model_dump() for c in f.config])
        postgres_client.add(dbf)
        postgres_client.commit()


def read_queue(user_id: int, song_id: str, filter_id: int | None, postgres_client: Session):
    # check if user has queue
    if filter_id is None:
        dbf = None
    else:
        dbf = postgres_client.query(DBFilter).filter(and_(
            DBFilter.user_id == user_id,
            DBFilter.id == filter_id
        )).first()
        if dbf is None:
            raise HTTPException(status_code=404, detail="User doesn't have this filter")

    # check if song exists
    # if not then start scrape
    db_seed_song = postgres_client.get(DBSong, song_id)
    db_song_data = postgres_client.get(DBSongData, song_id)
    print(db_seed_song, db_song_data)
    if db_seed_song is None:
        celery_app.send_task("music", queue="music", args=[song_id])
        return SongQueue(
            seed_song_id=song_id,
            scrape=False,
            songs=[]
        )
    """
    Strat
    get all songs
    filter out where user doesnt have 
    """
    mq = MusicQuery(user_id, postgres_client)
    songs = mq.get_songs(db_seed_song.id)
    has_scraped = db_song_data and db_song_data.type == "ready"
    # if enough songs then return them
    print(len(songs))
    if len(songs) >= MIN_QUEUE_SONGS:
        return SongQueue(
            seed_song_id=song_id,
            scrape=has_scraped,
            songs=songs
        )
    # songs hasnt been scrapped yet
    elif db_song_data is None:
        celery_app.send_task("music", queue="music", args=[song_id])
        return SongQueue(
            seed_song_id=song_id,
            scrape=False,
            songs=songs
        )

    # if still no enough songs then look at

    return SongQueue(
        seed_song_id=song_id,
        scrape=True,
        songs=songs
    )

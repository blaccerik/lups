from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from database.models import DBFilter, DBSong, DBArtist, DBSongQueue
from schemas.music_schema import QueuePrevious, Song, Artist
from services.music.song_service import read_song
from utils.helper_functions import dbfilter_to_filter
from utils.music_query import MusicQuery
from utils.scrapping import start_scrape_for_song


def update_song_queue_date(user_id: int, song_id: str, postgres_client: Session):
    dbsq = postgres_client.query(DBSongQueue).filter(and_(
        DBSongQueue.user_id == user_id,
        DBSongQueue.song_id == song_id
    )).first()
    if dbsq is None:
        dbsq = DBSongQueue(
            song_id=song_id,
            user_id=user_id
        )
    else:
        dbsq.date = datetime.now()
    postgres_client.add(dbsq)
    postgres_client.commit()


def read_queue(user_id: int, song_id: str, filter_id: int | None, postgres_client: Session) -> List[Song]:
    # check if user has filter
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
    if db_seed_song is None:
        start_scrape_for_song(song_id, postgres_client)
        raise HTTPException(status_code=404, detail="Song not found")
    elif db_seed_song.status == "working":
        raise HTTPException(status_code=404, detail="Song not found")

    # init queue
    _filter = dbfilter_to_filter(dbf)
    mq = MusicQuery(user_id, song_id, _filter, postgres_client)
    songs = mq.get_filtered_songs()
    update_song_queue_date(user_id, song_id, postgres_client)
    return songs


def read_previous(user_id: int, postgres_client: Session) -> List[QueuePrevious]:
    dbsq_list = postgres_client.query(DBSongQueue).filter(
        DBSongQueue.user_id == user_id
    ).order_by(desc(DBSongQueue.date)).limit(10).all()
    result = []
    for dbsq in dbsq_list:
        sid = dbsq.song_id
        song = read_song(sid, postgres_client)
        result.append(QueuePrevious(
            song=song,
            hidden=dbsq.hidden
        ))
    return result


def read_new_songs(postgres_client: Session) -> List[Song]:
    db_songs = postgres_client.query(DBSong).order_by(DBSong.date.desc()).limit(10)[::-1]
    songs = []
    for dbs in db_songs:
        if dbs.artist_id is None:
            a = None
        else:
            dba = postgres_client.get(DBArtist, dbs.artist_id)
            a = Artist(
                id=dba.id,
                name=dba.name
            )
        song = Song(
            id=dbs.id,
            title=dbs.title,
            length=dbs.length,
            artist=a,
            type=dbs.type
        )
        songs.append(song)
    return songs

from typing import List

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBFilter, DBSong, DBSongQueue
from schemas.music import Song, PreviousSongQueue
from utils.celery_config import celery_app
from utils.helper_functions import dbfilter_to_filter
from utils.music_query import MusicQuery

PREVIOUS_QUEUE_LIMIT = 5

def _update_song_queue(user_id: int, song_id: str, count: int, postgres_client: Session):
    dbsq = postgres_client.get(DBSongQueue, (song_id, user_id))
    if dbsq is None:
        dbsq = DBSongQueue(
            song_id=song_id,
            user_id=user_id,
            count=count
        )
    else:
        dbsq.count = dbsq.count + count
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
        celery_app.send_task("find_new_songs", args=[song_id], queue="music:1")
        raise HTTPException(status_code=404, detail="Song not found")

    # init queue
    filter_ = dbfilter_to_filter(dbf)
    mq = MusicQuery(user_id, song_id, filter_, postgres_client)
    songs = mq.get_filtered_songs()
    _update_song_queue(user_id, song_id, len(songs), postgres_client)
    return songs


def read_previous(user_id: int, postgres_client: Session) -> List[PreviousSongQueue]:
    dbsq_list = postgres_client.query(DBSongQueue).filter(
        DBSongQueue.user_id == user_id
    ).all()
    return [PreviousSongQueue(song_id=dbsq.song_id, count=dbsq.count) for dbsq in dbsq_list]

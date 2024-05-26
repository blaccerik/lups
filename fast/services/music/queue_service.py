from typing import List

import requests
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBFilter, DBSong, DBSongQueue
from schemas.music_schema import SongQueueResult, SongQueue, StatusType
from utils.helper_functions import dbfilter_to_filter
from utils.music_query import MusicQuery
from utils.scrapping import start_scrape_for_song

PREVIOUS_QUEUE_LIMIT = 5


def _is_song_id_valid(song_id: str):
    # hack by https://gist.github.com/tonY1883/a3b85925081688de569b779b4657439b
    url = f"https://img.youtube.com/vi/{song_id}/mqdefault.jpg"
    response = requests.head(url, allow_redirects=True, timeout=3)
    return response.status_code == 200


def _update_song_queue(user_id: int, song_id: str, song_nr: int, postgres_client: Session):
    dbsq = postgres_client.get(DBSongQueue, (song_id, user_id))
    if dbsq is None:
        dbsq = DBSongQueue(
            song_id=song_id,
            user_id=user_id,
            song_nr=song_nr
        )
    else:
        dbsq.song_nr = dbsq.song_nr + song_nr
    postgres_client.add(dbsq)
    postgres_client.commit()


def read_queue(user_id: int, song_id: str, filter_id: int | None, postgres_client: Session) -> SongQueue:
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
        if _is_song_id_valid(song_id):
            start_scrape_for_song(song_id, postgres_client)
            return SongQueue(songs=[], status=StatusType.working)
        else:
            raise HTTPException(status_code=404, detail="Song not found")
    elif db_seed_song.status == "working":
        return SongQueue(songs=[], status=StatusType.working)

    # init queue
    _filter = dbfilter_to_filter(dbf)
    mq = MusicQuery(user_id, song_id, _filter, postgres_client)
    songs = mq.get_filtered_songs()
    _update_song_queue(user_id, song_id, len(songs), postgres_client)
    return SongQueue(songs=songs, status=StatusType.ready)


def read_previous(user_id: int, postgres_client: Session) -> List[SongQueueResult]:
    dbsq_list = postgres_client.query(DBSongQueue).filter(
        DBSongQueue.user_id == user_id
    ).all()
    return [SongQueueResult(
        song_nr=dbsq.song_nr,
        hidden=dbsq.hidden,
        song_id=dbsq.song_id
    ) for dbsq in dbsq_list]

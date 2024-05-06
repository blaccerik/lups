import logging
import queue
import time
from collections import deque
from functools import wraps

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBReaction, DBSong, DBArtist, DBSongData, DBSongRelationV1
from schemas.music import Song, Artist, SongQueue, SongWrapper

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def log_time(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f'Function {func.__name__.rjust(24)} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


class MusicQuery:
    MAX_RESULTS_SIZE = 3000
    YIELD_PER = 256

    def __init__(self, user_id, song_id, postgres_client: Session):
        self.postgres_client = postgres_client
        self.user_id = user_id
        self.song_id = song_id

    @log_time
    def test(self):
        r = []
        for dbrv1, dbr in self.postgres_client.query(DBSongRelationV1, DBReaction).join(
                DBReaction,
                and_(
                    DBReaction.song_id == DBSongRelationV1.child_song_id,
                    DBReaction.user_id == self.user_id
                ), isouter=True
        ).yield_per(self.YIELD_PER):
            r.append(dbrv1)
        print(len(r))

    @log_time
    def get_mapping(self):
        result = {}
        banned = set()
        for dbrv1, dbr in self.postgres_client.query(DBSongRelationV1, DBReaction).join(
                DBReaction,
                and_(
                    DBReaction.song_id == DBSongRelationV1.child_song_id,
                    DBReaction.user_id == self.user_id
                ), isouter=True
        ).yield_per(self.YIELD_PER):
            cid = dbrv1.child_song_id
            pid = dbrv1.parent_song_id
            if cid in result:
                result[cid].append(pid)
            else:
                result[cid] = [pid]
            if dbr:
                banned.add(cid)
        return result, banned

    @log_time
    def get_ids(self) -> list:
        result = []
        song_map, banned = self.get_mapping()
        queue = deque()
        queue.append(self.song_id)
        searched = {self.song_id}
        while queue:
            song_id = queue.pop()
            for connection in song_map[song_id]:
                if connection in searched:
                    continue
                searched.add(connection)
                queue.append(connection)
                if connection in banned:
                    continue
                result.append(connection)
                if len(result) >= self.MAX_RESULTS_SIZE:
                    return result
        return result


    @log_time
    def ids_to_songs(self, ids):
        result = []
        for dbs, dba, dbsd in self.postgres_client.query(
            DBSong, DBArtist, DBSongData
        ).join(
            DBArtist, DBArtist.id == DBSong.artist_id, isouter=True
        ).join(
            DBSongData, DBSongData.id == DBSong.id, isouter=True
        ).filter(
            DBSong.id.in_(ids)
        ).all():

            has_audio = False
            artist = None if dba is None else Artist(
                id=dba.id,
                name=dba.name
            )
            result.append(SongWrapper(
                distance=1,
                song=Song(
                    id=dbs.id,
                    title=dbs.title,
                    length=dbs.length,
                    type=dbs.type,
                    has_audio=has_audio,
                    artist=artist
                )
            ))

        ssd = self.postgres_client.get(DBSongData, self.song_id)
        return SongQueue(
            seed_song_id=self.song_id,
            scrape=ssd is not None,
            songs=result
        )
        # print(r[0])
        # print("all relos", len(r), len(ids))
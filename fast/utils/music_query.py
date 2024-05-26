import logging
import time
from collections import deque
from functools import wraps
from typing import List

from sqlalchemy.orm import Session

from database.models import DBReaction, DBSong, DBArtist, DBSongRelationV2
from schemas.music_schema import Song, Artist, Filter

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
    MIN_RESULTS_SIZE = 100
    YIELD_PER = 256

    def __init__(self, user_id: int, song_id: str, f: Filter, postgres_client: Session):
        self.postgres_client = postgres_client
        self.user_id = user_id
        self.song_id = song_id
        self.filter = f

    @log_time
    def _get_mapping3(self):
        result = {}
        banned = set()
        for dbrv2 in self.postgres_client.query(DBSongRelationV2.id).yield_per(self.YIELD_PER):
            key = dbrv2.id
            id1 = key[:11]
            id2 = key[11:]
            if id1 in result:
                result[id1].append(id2)
            else:
                result[id1] = [id2]
            if id2 in result:
                result[id2].append(id1)
            else:
                result[id2] = [id1]

        for dbr in self.postgres_client.query(DBReaction.song_id).filter(DBReaction.user_id == self.user_id).all():
            banned.add(dbr.song_id)
        return result, banned

    @log_time
    def _get_ids3(self):
        result = []
        song_map, banned = self._get_mapping3()
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
                if len(result) >= self.MIN_RESULTS_SIZE:
                    yield result
                    result = []
        yield result

    def _ids_to_song_songs(self, ids) -> List[Song]:
        result = []
        for dbs, dba in self.postgres_client.query(
                DBSong, DBArtist
        ).join(
            DBArtist, DBArtist.id == DBSong.artist_id, isouter=True
        ).filter(
            DBSong.id.in_(ids)
        ).all():
            artist = None if dba is None else Artist(
                id=dba.id,
                name=dba.name
            )
            result.append(Song(
                id=dbs.id,
                title=dbs.title,
                length=dbs.length,
                type=dbs.type,
                artist=artist
            ))
        return result

    def _normalize_text(self, text: str):
        remove = ["(", ")", "[", "]", "'", '"', ".", ","]
        text = text.lower()
        for r in remove:
            text = text.replace(r, "")
        return text

    def _filter_songs(self, songs: List[Song]) -> List[Song]:
        result = []
        bad_types = ["MUSIC_VIDEO_TYPE_UGC"]
        for song in songs:

            # todo ugc include normal videos and music
            # NEXUS - Nii Kuum OtFAdJmUzZ8
            # Fix - Jaanipäev + sõnad mX97wSdyQH4
            # Has Generative AI Already Peaked? - Computerphile dDUC-LqVrPU
            if song.type in bad_types:
                continue

            for fc in self.filter.config:
                text: str = song.title if fc.target_title else song.artist.name
                text = self._normalize_text(text)
                word = fc.word
                if fc.include and word not in text:
                    break
                elif not fc.include and word in text:
                    break
            else:
                result.append(song)
        return result

    @log_time
    def get_filtered_songs(self) -> List[Song]:
        result = []
        for song_ids in self._get_ids3():
            # todo id to song takes 80% of the time
            songs = self._ids_to_song_songs(song_ids)
            filtered_songs = self._filter_songs(songs)
            result.extend(filtered_songs)
            if len(result) >= self.MIN_RESULTS_SIZE:
                break
        return result[:self.MIN_RESULTS_SIZE]

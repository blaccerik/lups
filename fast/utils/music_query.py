import logging
import time
from functools import wraps
import queue

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBReaction, DBSong, DBArtist, DBSongData, DBSongRelationV1
from schemas.music import Similarity, Song, Artist

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
        logger.info(f'Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


class MusicQuery:

    def __init__(self, user_id, postgres_client: Session):
        self.postgres_client = postgres_client
        self.user_id = user_id

    @log_time
    def get_songs(self, seed_song_id: str):
        # slow query
        MAX_RESULTS_SIZE = 40
        tries = 1000
        results = []
        q = queue.PriorityQueue()
        q.put((1, seed_song_id))
        searched_songs = set()
        while not q.empty() and tries:
            tries -= 1
            distance, search_song_id = q.get()
            for dbsr in self.postgres_client.query(DBSongRelationV1).filter(and_(
                DBSongRelationV1.parent_song_id == search_song_id
            )).yield_per(32):
                child_song_id = dbsr.child_song_id
                # update queue
                if child_song_id not in searched_songs:
                    q.put((distance + dbsr.distance, child_song_id))
                    searched_songs.add(child_song_id)

                # if user has reaction
                dbr = self.postgres_client.query(DBReaction).filter(and_(
                    DBReaction.song_id == child_song_id,
                    DBReaction.user_id == self.user_id
                )).first()
                if dbr:
                    continue
                # get song, song data, and artist
                dbs, dba, dbsd = self.postgres_client.query(DBSong, DBArtist, DBSongData).filter(
                    DBSong.id == child_song_id,
                ).outerjoin(
                    DBArtist,
                    DBArtist.id == DBSong.id
                ).outerjoin(
                    DBSongData,
                    DBSongData.id == DBSong.id
                ).first()
                artist = None
                if dba:
                    artist = Artist(
                        id=dba.id,
                        name=dba.name
                    )
                song = Song(
                    id=dbs.id,
                    title=dbs.title,
                    length=dbs.length,
                    type=dbs.type,
                    has_audio=False,
                    artist=artist
                )
                results.append(song)
                if len(results) >= MAX_RESULTS_SIZE:
                    return results
        return results


        # self.postgres_client.ge

        # for dbsr in self.postgres_client.query(DBSongRelation).filter(
        #         DBSongRelation.parent_song_id == seed_song_id
        # ).yield_per(32):
        #
        #     child_song_id = dbsr.child_song_id
        #
        #     dbr = self.postgres_client.query(DBReaction).filter(and_(
        #         DBReaction.song_id == child_song_id,
        #         DBReaction.user_id == self.user_id
        #     )).first()
        #     if dbr:
        #         continue
        #     dbs, dba, dbsd = self.postgres_client.query(DBSong, DBArtist, DBSongData).filter(and_(
        #         DBSong.id == child_song_id,
        #         DBSong.artist_id == DBArtist.id
        #     )).outerjoin(
        #         DBSongData,
        #         DBSongData.id == DBSong.id
        #     ).first()
        #     artist = None
        #     if dba:
        #         artist = Artist(
        #             id=dba.id,
        #             name=dba.name
        #         )
        #
        #     song = Song(
        #         id=dbs.id,
        #         title=dbs.title,
        #         length=dbs.length,
        #         type=dbs.type,
        #         has_audio=False,
        #         artist=artist
        #     )
        #     sim = Similarity(
        #         same_artist=db_seed_song.artist_id == dbs.artist_id,
        #         same_genre=True,
        #         song=song
        #     )
        #     results.append(sim)
        # return results

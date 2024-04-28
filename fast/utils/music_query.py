import logging
import time
from functools import wraps

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBSongRelationV1, DBReaction, DBSong, DBArtist, DBScrapeV1
from schemas.music import Similarity, Song, Artist

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

        db_seed_song = self.postgres_client.get(DBSong, seed_song_id)
        results = []
        for dbsr in self.postgres_client.query(DBSongRelationV1).filter(
                DBSongRelationV1.parent_song_id == seed_song_id
        ).yield_per(32):

            print(dbsr)

            child_song_id = dbsr.child_song_id

            dbr = self.postgres_client.query(DBReaction).filter(and_(
                DBReaction.song_id == child_song_id,
                DBReaction.user_id == self.user_id
            )).first()
            if dbr:
                continue
            dbs, dba, dbsv1 = self.postgres_client.query(DBSong, DBArtist, DBScrapeV1).filter(and_(
                DBSong.id == child_song_id,
                DBSong.artist_id == DBArtist.id
            )).outerjoin(
                DBScrapeV1,
                DBScrapeV1.id == DBSong.id
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
            sim = Similarity(
                same_artist=db_seed_song.artist_id == dbs.artist_id,
                same_genre=True,
                song=song
            )
            results.append(sim)
        print(len(results))
        return results

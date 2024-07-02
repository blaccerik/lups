import json

from database.models import DBUser, DBReaction, DBSong, DBSongRelationV1, DBSongRelationV2, DBFilter
from database.postgres_database import SessionLocal
from schemas.music_schema import Filter, FilterConfig
from utils.helper_functions import dbfilter_to_filter
from utils.music_query import MusicQuery


def test1(postgres_client):
    print("all songs", postgres_client.query(DBSong).count())
    print("all relations", postgres_client.query(DBSongRelationV1).count())
    print("all relations2", postgres_client.query(DBSongRelationV2).count())
    print("banned", postgres_client.query(DBReaction).count())
    f = Filter(
        id=1,
        name="test",
        config=[
            FilterConfig(
                include=False,
                target_title=True,
                word="e"
            )
        ]
    )

    song_id = "jRqhGC5vgC0"
    mq = MusicQuery(1, song_id, f, postgres_client)
    sq = mq.get_filtered_songs()
    # for s in sq.songs:
    #     print(s.song)
    print(len(sq.songs))
    print(sq.songs[0])
    for s in sq.songs:
        postgres_client.add(DBReaction(
            song_id=s.song.id,
            user_id=1,
            type="listened",
            duration=1
        ))
    postgres_client.commit()


if __name__ == '__main__':
    postgres_client = SessionLocal()
    try:
        dbu = postgres_client.get(DBUser, 1)
        if dbu is None:
            postgres_client.add(DBUser(
                id=1,
                google_id="1",
                name="1"
            ))
            postgres_client.commit()

        test1(postgres_client)
    finally:
        postgres_client.close()

import time

from database.models import DBUser, DBReaction, DBSong, DBSongRelationV1, DBSongRelationV2
from database.postgres_database import SessionLocal
from utils.music_query import MusicQuery


def test1(postgres_client):
    print("all songs", postgres_client.query(DBSong).count())
    print("all relations", postgres_client.query(DBSongRelationV1).count())
    print("all relations2", postgres_client.query(DBSongRelationV2).count())
    print("banned", postgres_client.query(DBReaction).count())

    song_id = "jRqhGC5vgC0"
    mq = MusicQuery(1, song_id, postgres_client)
    # ids = mq.get_ids()
    # print("ids", len(ids))
    # ids2 = mq.get_ids2()
    # print("ids2", len(ids2))
    # ids3 = mq.get_ids3()
    # print("ids3", len(ids3))
    # print(len(set(ids).intersection(set(ids2))))
    # print(len(set(ids).intersection(set(ids3))))


    # songs = mq.ids_to_songs(ids)
    # print("song", songs.songs[0])
    # print("song nr", len(songs.songs))
    # for s in ids:
    #     postgres_client.add(DBReaction(
    #         song_id=s,
    #         user_id=1,
    #         type="listened",
    #         duration=1
    #     ))
    # postgres_client.commit()

    song_id = "jRqhGC5vgC0"
    mq = MusicQuery(0, song_id, postgres_client)
    ids = mq.get_ids()
    print("ids", len(ids))
    ids2 = mq.get_ids2()
    print("ids2", len(ids2))
    ids3 = mq.get_ids3()
    print("ids3", len(ids3))
    print(len(set(ids).intersection(set(ids2))))
    print(len(set(ids).intersection(set(ids3))))

    """
    INFO:utils.music_query:Function              get_mapping Took 0.7968 seconds
    INFO:utils.music_query:Function                  get_ids Took 0.7988 seconds
    INFO:utils.music_query:Function             get_mapping2 Took 0.6833 seconds
    INFO:utils.music_query:Function                 get_ids2 Took 0.6843 seconds
    INFO:utils.music_query:Function             get_mapping3 Took 0.1551 seconds
    INFO:utils.music_query:Function                 get_ids3 Took 0.1572 seconds
    """
    return


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


from database.models import DBUser, DBReaction, DBSong, DBSongRelationV1
from database.postgres_database import SessionLocal
from utils.music_query import MusicQuery


def test1(postgres_client):

    print("all songs", len(postgres_client.query(DBSong).all()))
    print("all relations", len(postgres_client.query(DBSongRelationV1).all()))

    song_id = "jRqhGC5vgC0"
    mq = MusicQuery(1, song_id, postgres_client)
    ids = mq.get_ids()
    songs = mq.ids_to_songs(ids)
    print("song", songs.songs[0])
    print("song nr", len(songs.songs))
    for s in ids:
        postgres_client.add(DBReaction(
            song_id=s,
            user_id=1,
            type="listened",
            duration=1
        ))
    postgres_client.commit()

    # test if are similar
    #
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


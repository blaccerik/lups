import random

from sqlalchemy.orm import Session

from database.models import DBSong, DBSongData
from util.downloadv2 import add_artist, get_result, add_song, add_connections, add_connections2, Adder
from util.log_time import log_time


@log_time
def select_random_song(postgres_client: Session):
    dbsongs = postgres_client.query(DBSong).all()
    dbsong = random.choice(dbsongs)
    return dbsong.id


@log_time
def download_by_song_id(song_id: str, postgres_client: Session):
    # check if needs to download
    db_song_data = postgres_client.get(DBSongData, song_id)
    if db_song_data is not None:
        return 0, 0, 0, 0

    # download
    result = get_result(song_id)
    if result is None:
        return -1, -1, -1, -1

    new_artists = 0
    new_songs = 0
    new_connections = 0
    new_connections2 = 0
    for track in result["tracks"]:
        # parse artist
        artist_dict = track["artists"][0]
        new_artists += add_artist(artist_dict["id"], artist_dict["name"], postgres_client)

        # parse length
        length: str = track["length"]
        m, s = length.split(":")
        m = int(m)
        s = int(s)
        number = m * 60 + s

        # parse song
        new_songs += add_song(
            track["videoId"],
            track["title"][:100],
            number,
            artist_dict["id"],
            track["videoType"],
            track["thumbnail"][-1]["url"],
            postgres_client
        )

        new_connections += add_connections(song_id, track["videoId"], postgres_client)

        new_connections2 += add_connections2(song_id, track["videoId"], postgres_client)

    # update song state database
    postgres_client.add(DBSongData(
        id=song_id,
        type="ready"
    ))
    postgres_client.commit()
    return new_artists, new_songs, new_connections, new_connections2


@log_time
def download_by_song_id2(song_id: str, postgres_client: Session):
    # check if needs to download
    db_song_data = postgres_client.get(DBSongData, song_id)
    if db_song_data is not None:
        return 0, 0, 0

    # download
    result = get_result(song_id)
    if result is None:
        return 0, 0, 0
    a = Adder(postgres_client)
    for track in result["tracks"]:
        # parse artist
        artist_dict = track["artists"][0]

        a.add_artist(artist_dict["id"], artist_dict["name"])

        # parse length
        length: str = track["length"]
        m, s = length.split(":")
        m = int(m)
        s = int(s)
        number = m * 60 + s

        # parse song
        a.add_song(
            track["videoId"],
            track["title"][:100],
            number,
            artist_dict["id"],
            track["videoType"],
            track["thumbnail"][-1]["url"],
        )
        a.add_connection(song_id, track["videoId"])
    a.add_to_db()
    # update song state database
    postgres_client.add(DBSongData(
        id=song_id,
        type="ready"
    ))
    postgres_client.commit()
    return len(a.artists), len(a.songs), len(a.connections)
    # return new_artists, new_songs, new_connections, new_connections2

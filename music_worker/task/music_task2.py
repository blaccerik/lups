import random
import time

from sqlalchemy.orm import Session

from database.models import DBSong, DBSongData
from util.downloadv2 import add_artist, get_result, add_song, add_connections, add_connections2
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
    times = [0,0,0,0]
    for track in result["tracks"]:
        # parse artist
        artist_dict = track["artists"][0]
        t1 = time.time()
        new_artists += add_artist(artist_dict["id"], artist_dict["name"], postgres_client)
        t2 = time.time()
        times[0] += t2 - t1
        # parse length
        length: str = track["length"]
        m, s = length.split(":")
        m = int(m)
        s = int(s)
        number = m * 60 + s

        # parse song
        t1 = time.time()
        new_songs += add_song(
            track["videoId"],
            track["title"][:100],
            number,
            artist_dict["id"],
            track["videoType"],
            track["thumbnail"][-1]["url"],
            postgres_client
        )
        t2 = time.time()
        times[1] += t2 - t1

        t1 = time.time()
        new_connections += add_connections(song_id, track["videoId"], postgres_client)
        t2 = time.time()
        times[2] += t2 - t1

        t1 = time.time()
        new_connections2 += add_connections2(song_id, track["videoId"], postgres_client)
        t2 = time.time()
        times[3] += t2 - t1

    # update song state database
    postgres_client.add(DBSongData(
        id=song_id,
        type="ready"
    ))
    postgres_client.commit()
    print(times)
    return new_artists, new_songs, new_connections, new_connections2

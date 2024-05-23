import random

from sqlalchemy.orm import Session

from database.models import DBSong, DBSongData
from schemas.main import Result
from util.downloadv2 import get_result, Adder
from util.log_time import log_time


@log_time
def select_random_song(postgres_client: Session) -> str:
    dbs_list = (postgres_client.query(DBSong.id).filter(
        DBSong.type != "MUSIC_VIDEO_TYPE_UGC"
    ).all())
    if len(dbs_list) == 0:
        return "dQw4w9WgXcQ"
    dbs = random.choice(dbs_list)
    return dbs.id


@log_time
def find_new_songs_by_song_id(song_id: str, postgres_client: Session) -> Result:
    # check if needs to download
    db_song_data = postgres_client.get(DBSongData, song_id)
    if db_song_data is not None:
        return Result(artist_image_ids=[], songs={})

    # download
    result = get_result(song_id)
    if result is None:
        return Result(artist_image_ids=[], songs={})
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
    return a.get_results()

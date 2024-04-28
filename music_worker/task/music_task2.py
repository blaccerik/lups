from sqlalchemy.orm import Session

from database.models import DBSong
from util.downloadv2 import add_artist, get_result, add_song
from util.log_time import log_time


@log_time
def download_by_song_id(song_id: str, postgres_client: Session):

    # check if needs to download
    if postgres_client.get(DBSong, song_id):
        return 0, 0

    # download
    result = get_result(song_id)
    if result is None:
        return -1, -1

    new_artists = 0
    new_songs = 0
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
            song_id,
            track["videoId"],
            track["title"][:100],
            number,
            artist_dict["id"],
            track["videoType"],
            track["thumbnail"][-1]["url"],
            postgres_client
        )

    return new_artists, new_songs

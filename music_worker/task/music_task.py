import logging
import random
from typing import List

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.models import DBArtist, DBSong, DBSongRelationV1, DBReaction
from schemas.main import Artist, Song
from util.download import download_channel_image, download_song, download_song_image, download_watch
from util.log_time import log_time

logger = logging.getLogger(__name__)


@log_time
def get_song_watch_data(seed_video_id) -> tuple:
    result = download_watch(seed_video_id)
    songs = []
    artists = {}
    images = {}
    seed_song = None
    for track in result["tracks"]:
        artist_dict = track["artists"][0]
        key = artist_dict["id"]
        if key not in artists and key is not None:
            artists[key] = Artist(
                id=key,
                name=artist_dict["name"]
            )

        length: str = track["length"]

        # parse length
        m, s = length.split(":")
        m = int(m)
        s = int(s)
        number = m * 60 + s
        # find artist
        if key:
            artist = artists[key]
        else:
            artist = None
        image_link = track["thumbnail"][-1]["url"]
        images[track["videoId"]] = image_link
        title = track["title"][:100]
        song = Song(
            id=track["videoId"],
            title=title,
            length=number,
            artist=artist,
            type=track["videoType"],
        )
        songs.append(song)
        if track["videoId"] == seed_video_id:
            seed_song = song

    return songs, list(artists.values()), images, seed_song


@log_time
def add_artists_to_db(artists: List[Artist], postgres_client: Session):
    for artist in artists:
        dba = postgres_client.query(DBArtist).get(artist.id)
        if dba:
            continue
        dba = DBArtist()
        dba.id = artist.id
        dba.name = artist.name
        postgres_client.add(dba)
        postgres_client.commit()
        download_channel_image(artist.id)


def add_song_to_db(song: Song, song_images: dict, postgres_client: Session) -> DBSong:
    dbs = postgres_client.query(DBSong).get(song.id)
    if dbs:
        return dbs
    dbs = DBSong()
    dbs.id = song.id
    dbs.title = song.title
    dbs.length = song.length
    if song.artist:
        dbs.artist_id = song.artist.id
    dbs.type = song.type
    postgres_client.add(dbs)
    postgres_client.commit()
    download_song_image(song.id, song_images)
    download_song(song.id)
    return dbs


@log_time
def add_songs_to_db(seed_song: Song, songs: List[Song], song_images: dict, postgres_client: Session):
    if seed_song is None:
        logger.error("seed song is None")
        return
    db_seed_song = add_song_to_db(seed_song, song_images, postgres_client)

    for song in songs:
        db_song = add_song_to_db(song, song_images, postgres_client)

        # skip if same song
        if song.id == seed_song.id:
            continue
        dbs = postgres_client.query(DBSongRelationV1).filter_by(
            child_song_id=song.id,
            parent_song_id=seed_song.id
        ).first()
        if dbs:
            continue
        dbsr = DBSongRelationV1()
        dbsr.child_song_id = song.id
        dbsr.parent_song_id = seed_song.id
        dbsr.same_artist = db_seed_song.artist_id == db_song.artist_id
        dbsr.same_genre = True
        postgres_client.add(dbsr)
        dbsr2 = DBSongRelationV1()
        dbsr2.parent_song_id = song.id
        dbsr2.child_song_id = seed_song.id
        dbsr2.same_artist = db_seed_song.artist_id == db_song.artist_id
        dbsr2.same_genre = True
        postgres_client.add(dbsr2)
    postgres_client.commit()


@log_time
def get_next_seed_song_id(postgres_client: Session) -> str:
    # Query to count the number of connections for each song and sort by the count
    song_connections = postgres_client.query(
        DBSong.id,
        func.count(DBSongRelationV1.id).label('connection_count')
    ).outerjoin(
        DBSongRelationV1, DBSong.id == DBSongRelationV1.parent_song_id
    ).group_by(
        DBSong.id
    ).order_by(
        'connection_count'
    ).limit(100).all()
    for a, b in song_connections:
        print(a, b)
    sc = random.choice(song_connections)
    logger.info(f"selected: {sc[0]} with {sc[1]} connections")
    return sc[0]


@log_time
def get_next_song_by_user(user_id: int, postgres_client: Session) -> str:
    # Query song and its reaction
    result = postgres_client.query(DBSong, DBReaction).filter(and_(
        DBSong.id == DBReaction.song_id,
        DBReaction.user_id == user_id
    )).all()
    pass

import logging
import os
import platform
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ytmusicapi import YTMusic

from database.models import DBSong, DBArtist, DBSongRelationV1

operating_system = platform.system()
if operating_system == 'Windows':
    MUSIC_DATA = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/music_data"
else:
    MUSIC_DATA = "/usr/src/app/music_data"

DOWNLOAD_TIMEOUT = 0.5
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.info(MUSIC_DATA)

# check if folders are there
path1 = f"{MUSIC_DATA}/artist_images"
if not os.path.exists(path1):
    os.mkdir(path1)
    logger.error(path1)

path2 = f"{MUSIC_DATA}/song_images"
if not os.path.exists(path2):
    os.mkdir(path2)
    logger.error(path2)

path3 = f"{MUSIC_DATA}/songs"
if not os.path.exists(path3):
    os.mkdir(path3)
    logger.error(path3)


def get_result(song_id):
    ytmusic = YTMusic("oauth.json")
    try:
        result = ytmusic.get_watch_playlist(
            videoId=song_id,
            radio=True
        )
    except Exception as e:
        logger.error(e)
        return None
    time.sleep(DOWNLOAD_TIMEOUT)
    return result


def add_artist(artist_id, artist_name, postgres_client: Session) -> int:
    dba = postgres_client.get(DBArtist, artist_id)
    if dba:
        return 0

    dba = DBArtist(
        name=artist_name,
        id=artist_id
    )
    postgres_client.add(dba)
    postgres_client.commit()

    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/artist_images/{artist_id}.jpg"):
        logger.error(f"image exists: {artist_id}")
        return 1
    response = requests.get(f"https://music.youtube.com/channel/{artist_id}")
    if response.status_code != 200:
        logger.error(f"error getting channel")
        return 1
    soup = BeautifulSoup(response.content, 'html.parser')
    image_tag = soup.find("meta", {"property": "og:image"})
    if not image_tag:
        logger.error(f"error getting channel image tag")
        return 1
    image_url = image_tag.get("content")
    res = requests.get(image_url)
    if res.status_code != 200:
        logger.error(f"error downloading channel image")
        return 1
    with open(f"{MUSIC_DATA}/artist_images/{artist_id}.jpg", "wb") as file:
        file.write(res.content)
    time.sleep(DOWNLOAD_TIMEOUT)
    return 1


def add_song(seed_song_id, song_id, song_title, number, artist_id, song_type, image_link, postgres_client: Session):
    dbs = postgres_client.get(DBSong, song_id)
    if dbs:
        return 0

    dbs = DBSong(
        id=song_id,
        title=song_title,
        length=number,
        artist_id=artist_id,
        type=song_type
    )
    postgres_client.add(dbs)

    dbsr = DBSongRelationV1()
    dbsr.child_song_id = song_id
    dbsr.parent_song_id = seed_song_id
    postgres_client.add(dbsr)

    dbsr2 = DBSongRelationV1()
    dbsr2.parent_song_id = song_id
    dbsr2.child_song_id = seed_song_id
    postgres_client.add(dbsr2)

    postgres_client.commit()

    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/song_images/{id}.jpg"):
        logger.error(f"image exists: {id}")
        return 1

    res = requests.get(image_link)
    if res.status_code != 200:
        logger.error(f"error downloading song image")
        return 1
    with open(f"{MUSIC_DATA}/song_images/{song_id}.jpg", "wb") as file:
        file.write(res.content)
    time.sleep(DOWNLOAD_TIMEOUT)
    return 1

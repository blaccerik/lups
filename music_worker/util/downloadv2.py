import json
import logging
import os
import platform
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from sqlalchemy import and_
from sqlalchemy.orm import Session
from ytmusicapi import YTMusic

from database.models import DBSong, DBArtist, DBSongData, DBSongRelationV1, DBSongRelationV2
from task.music_task import log_time

operating_system = platform.system()
if operating_system == 'Windows':
    MUSIC_DATA = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/music_data"
else:
    MUSIC_DATA = "/usr/src/app/music_data"
DOWNLOAD_IMAGES = False
DOWNLOAD_TIMEOUT = 0.5
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.info(MUSIC_DATA)
logger.info(DOWNLOAD_IMAGES)

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

path4 = f"{MUSIC_DATA}/song_json"
if not os.path.exists(path4):
    os.mkdir(path4)
    logger.error(path4)


@log_time
def add_all():
    result = []
    for f in os.listdir(MUSIC_DATA + "/song_json"):
        name = f.split(".")[0]
        result.append(name)
    return result

@log_time
def get_result(song_id):
    ytmusic = YTMusic("oauth.json")
    try:
        path = f"{MUSIC_DATA}/song_json/{song_id}.json"
        if os.path.exists(f"{MUSIC_DATA}/song_json/{song_id}.json"):
            logger.info(f"cached: {song_id}")
            with open(path, "r") as json_file:
                result = json.load(json_file)
        else:
            result = ytmusic.get_watch_playlist(
                videoId=song_id,
                radio=True
            )
            time.sleep(DOWNLOAD_TIMEOUT)
            with open(path, "w") as json_file:
                json.dump(result, json_file)
    except Exception as e:
        logger.error(e)
        return None
    return result


def add_artist(artist_id, artist_name, postgres_client: Session) -> int:
    if artist_id is None:
        return 0

    dba = postgres_client.get(DBArtist, artist_id)
    if dba:
        return 0

    dba = DBArtist(
        name=artist_name,
        id=artist_id
    )
    postgres_client.add(dba)
    postgres_client.commit()

    if not DOWNLOAD_IMAGES:
        return 1

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


def add_song(song_id, song_title, number, artist_id, song_type, image_link, postgres_client: Session):

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
    postgres_client.commit()

    if not DOWNLOAD_IMAGES:
        return 1

    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/song_images/{song_id}.jpg"):
        logger.error(f"image exists: {song_id}")
        return 1

    res = requests.get(image_link)
    if res.status_code != 200:
        logger.error(f"error downloading song image")
        return 1
    with open(f"{MUSIC_DATA}/song_images/{song_id}.jpg", "wb") as file:
        file.write(res.content)
    time.sleep(DOWNLOAD_TIMEOUT)
    return 1


def add_connections(seed_song_id, song_id, postgres_client: Session):
    if seed_song_id == song_id:
        return 0
    dbsr = postgres_client.get(DBSongRelationV1, (seed_song_id, song_id))
    if dbsr:
        return 0
    dbsr1 = DBSongRelationV1()
    dbsr1.child_song_id = song_id
    dbsr1.parent_song_id = seed_song_id
    postgres_client.add(dbsr1)

    dbsr2 = DBSongRelationV1()
    dbsr2.parent_song_id = song_id
    dbsr2.child_song_id = seed_song_id
    postgres_client.add(dbsr2)
    postgres_client.commit()
    return 2

def add_connections2(seed_song_id, song_id, postgres_client: Session):
    if seed_song_id == song_id:
        return 0
    key1 = seed_song_id + song_id
    key2 = song_id + seed_song_id
    dbsr = postgres_client.get(DBSongRelationV2, key1)
    if dbsr:
        return 0
    dbsr = postgres_client.get(DBSongRelationV2, key2)
    if dbsr:
        return 0
    dbsr = DBSongRelationV2(
        id=key1
    )
    postgres_client.add(dbsr)
    postgres_client.commit()
    return 1
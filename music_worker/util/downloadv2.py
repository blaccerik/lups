import json
import logging
import os
import platform
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ytmusicapi import YTMusic

from database.models import DBSong, DBArtist, DBSongRelationV2
from schemas.main import Result
from task.music_task import log_time

operating_system = platform.system()
if operating_system == 'Windows':
    MUSIC_DATA = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/music_data"
else:
    MUSIC_DATA = "/usr/src/app/music_data"
DOWNLOAD_IMAGES = True
DOWNLOAD_TIMEOUT = 0.5
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


@log_time
def download_artist_image_by_id(artist_id):
    if not DOWNLOAD_IMAGES:
        return

    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/artist_images/{artist_id}.jpg"):
        logger.error(f"image exists: {artist_id}")
        return
    response = requests.get(f"https://music.youtube.com/channel/{artist_id}")
    if response.status_code != 200:
        logger.error(f"error getting channel")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    image_tag = soup.find("meta", {"property": "og:image"})
    if not image_tag:
        logger.error(f"error getting channel image tag")
        return
    image_url = image_tag.get("content")
    res = requests.get(image_url)
    if res.status_code != 200:
        logger.error(f"error downloading channel image")
        return
    with open(f"{MUSIC_DATA}/artist_images/{artist_id}.jpg", "wb") as file:
        file.write(res.content)
    time.sleep(DOWNLOAD_TIMEOUT)
    return


@log_time
def download_song_image_by_link(song_id, image_link):
    if not DOWNLOAD_IMAGES:
        return

    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/song_images/{song_id}.jpg"):
        logger.error(f"image exists: {song_id}")
        return

    res = requests.get(image_link)
    if res.status_code != 200:
        logger.error(f"error downloading song image")
        return
    with open(f"{MUSIC_DATA}/song_images/{song_id}.jpg", "wb") as file:
        file.write(res.content)
    time.sleep(DOWNLOAD_TIMEOUT)
    return


class Adder:
    def __init__(self, postgres_client: Session):
        self.artists = {}
        self.song_images = {}
        self.songs = {}
        self.connections = {}
        self.postgres_client = postgres_client

    def add_to_db(self):
        self.postgres_client.add_all(self.artists.values())
        self.postgres_client.flush()
        self.postgres_client.add_all(self.songs.values())
        self.postgres_client.flush()
        self.postgres_client.add_all(self.connections.values())
        self.postgres_client.commit()

    def add_artist(self, artist_id, artist_name):
        if artist_id is None:
            return
        if self.postgres_client.get(DBArtist, artist_id):
            return
        if artist_id in self.artists:
            return
        dba = DBArtist(
            name=artist_name,
            id=artist_id
        )
        self.artists[artist_id] = dba

    def add_song(self, song_id, song_title, number, artist_id, song_type, image_link):

        if self.postgres_client.get(DBSong, song_id):
            return
        if song_id in self.songs:
            return
        dbs = DBSong(
            id=song_id,
            title=song_title,
            length=number,
            artist_id=artist_id,
            type=song_type
        )
        self.songs[song_id] = dbs
        self.song_images[song_id] = image_link

    def add_connection(self, seed_song_id, song_id):
        if seed_song_id == song_id:
            return
        key1 = seed_song_id + song_id
        key2 = song_id + seed_song_id
        dbsr = self.postgres_client.get(DBSongRelationV2, key1)
        if dbsr:
            return 0
        dbsr = self.postgres_client.get(DBSongRelationV2, key2)
        if dbsr:
            return 0
        if key1 in self.connections:
            return
        if key2 in self.connections:
            return

        dbsr = DBSongRelationV2(
            id=key1
        )
        self.connections[key1] = dbsr

    def get_results(self) -> Result:
        artists = [a.id for a in self.artists.values()]
        return Result(artist_image_ids=artists, songs=self.song_images)

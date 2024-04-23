import json
import logging
import os
import platform
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pytube import YouTube
from ytmusicapi import YTMusic

operating_system = platform.system()
if operating_system == 'Windows':
    MUSIC_DATA = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/music_data"
else:
    MUSIC_DATA = "/usr/src/app/music_data"
REAL_DOWNLOAD = False
DOWNLOAD_TIMEOUT = 0.5

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.info(MUSIC_DATA)
logger.info(f"REAL_DOWNLOAD: {REAL_DOWNLOAD}")


def download_watch(song_id: str) -> dict:
    if REAL_DOWNLOAD:
        ytmusic = YTMusic("oauth.json")
        result = ytmusic.get_watch_playlist(
            videoId=song_id,
            radio=True
        )
        time.sleep(DOWNLOAD_TIMEOUT)
    elif os.path.exists(f"{MUSIC_DATA}/song_json/{song_id}.json"):
        with open(f"{MUSIC_DATA}/song_json/{song_id}.json", "r") as json_file:
            result = json.load(json_file)
    else:
        ytmusic = YTMusic("oauth.json")
        result = ytmusic.get_watch_playlist(
            videoId=song_id,
            radio=True
        )
        with open(f"{MUSIC_DATA}/song_json/{song_id}.json", "w") as json_file:
            json.dump(result, json_file)
        time.sleep(DOWNLOAD_TIMEOUT)
    return result


def download_channel_image(id: str):
    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/artist_images/{id}.jpg"):
        logger.error(f"image exists: {id}")
        return
    if not REAL_DOWNLOAD:
        return
        # try to get image for channel
    response = requests.get(f"https://music.youtube.com/channel/{id}")
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
    with open(f"{MUSIC_DATA}/artist_images/{id}.jpg", "wb") as file:
        file.write(res.content)
    time.sleep(DOWNLOAD_TIMEOUT)


def download_song_image(id: str, song_images):
    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/song_images/{id}.jpg"):
        logger.error(f"image exists: {id}")
        return

    if not REAL_DOWNLOAD:
        return

    if id not in song_images:
        logger.error(f"{id} not in song_images")
        return
    url = song_images[id]
    res = requests.get(url)
    if res.status_code != 200:
        logger.error(f"error downloading song image")
        return
    with open(f"{MUSIC_DATA}/song_images/{id}.jpg", "wb") as file:
        file.write(res.content)
    time.sleep(DOWNLOAD_TIMEOUT)


def download_song(song_id: str):
    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/songs/{song_id}.mp3"):
        logger.error(f"song exists: {song_id}")
        return

    if not REAL_DOWNLOAD:
        return

    yt = YouTube(f"https://music.youtube.com/watch?v={song_id}")
    yt.streams.filter(only_audio=True).first().download(
        output_path=f"{MUSIC_DATA}/songs",
        filename=f"{song_id}.mp3"
    )
    time.sleep(DOWNLOAD_TIMEOUT)

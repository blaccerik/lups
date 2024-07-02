import json
import logging
import os
import platform
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic

from util.log_time import log_time

operating_system = platform.system()
if operating_system == 'Windows':
    MUSIC_DATA = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/music_data"
else:
    MUSIC_DATA = "/usr/src/app/music_data"
DOWNLOAD_IMAGES = True
DOWNLOAD_TIMEOUT = 0.5
logger = logging.getLogger(__name__)
logger.warning(MUSIC_DATA)
logger.warning(DOWNLOAD_IMAGES)

# check if folders are there
path1 = f"{MUSIC_DATA}/artist_images"
if not os.path.exists(path1):
    os.mkdir(path1)
    logger.error(path1)

path2 = f"{MUSIC_DATA}/song_images"
if not os.path.exists(path2):
    os.mkdir(path2)
    logger.error(path2)

path4 = f"{MUSIC_DATA}/song_json"
if not os.path.exists(path4):
    os.mkdir(path4)
    logger.error(path4)


@log_time
def download_scrape(song_id):
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


def download_song_image_by_link(song_id, image_link):
    if not DOWNLOAD_IMAGES:
        return
    # check if image exists
    if os.path.exists(f"{MUSIC_DATA}/song_images/{song_id}.jpg"):
        logger.error(f"image exists: {song_id}")
        return

    res = requests.get(image_link)
    if res.status_code != 200:
        logger.error(f"error downloading song image {song_id} {image_link}")
        return

    img = Image.open(BytesIO(res.content))
    w = img.width
    h = img.height
    # modify image if it's not square
    if w != h:
        s = min(w, h)
        img = img.crop((
            (w - s) // 2,
            (h - s) // 2,
            w - ((w - s) // 2),
            h - ((h - s) // 2)
        ))
    img.save(f"{MUSIC_DATA}/song_images/{song_id}.jpg")
    time.sleep(DOWNLOAD_TIMEOUT)
    return

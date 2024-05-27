import logging

from celery import Celery

from database.postgres_database import SessionLocal
from database.redis_database import REDIS_DATABASE_URI
from task.music_task2 import find_new_songs_by_song_id, select_random_song
from util.downloadv2 import download_artist_image_by_id, download_song_image_by_link

logger = logging.getLogger(__name__)

celery_app = Celery(
    'main_app',
    broker=REDIS_DATABASE_URI,
    backend=REDIS_DATABASE_URI,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
    timezone='Europe/Tallinn',
)

celery_app.conf.broker_transport_options = {
    'priority_steps': list(range(5)),
    'sep': ':',
    'queue_order_strategy': 'priority',
}


@celery_app.task(name="download_song_image")
def download_song_image(song_id: str, song_image_link: str):
    download_song_image_by_link(song_id, song_image_link)


@celery_app.task(name="download_artist_image")
def download_artist_image(artist_id: str):
    download_artist_image_by_id(artist_id)


@celery_app.task(name="find_new_songs")
def find_new_songs(song_id: str):
    postgres_client = SessionLocal()
    if song_id == "":
        song_id = select_random_song(postgres_client)
    print(song_id)
    results = find_new_songs_by_song_id(song_id, postgres_client)
    postgres_client.close()
    logger.warning(f"Songs: {len(results.songs)} Artists: {len(results.artist_image_ids)}")
    # start tasks
    for song_id, song_image_link in results.songs.items():
        celery_app.send_task("download_song_image", args=[song_id, song_image_link], queue="music", priority=4)
    for artist_id in results.artist_image_ids:
        celery_app.send_task("download_artist_image", args=[artist_id], queue="music", priority=4)
    return len(results.songs)

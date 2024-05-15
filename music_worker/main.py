import logging

from celery import Celery

from database.postgres_database import SessionLocal
from database.redis_database import REDIS_DATABASE_URI
from task.music_task2 import find_new_songs_by_song_id
from util.downloadv2 import download_song_by_id

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


@celery_app.task(name="download_song")
def download_song(song_id: str):
    download_song_by_id(song_id)
    return 1


@celery_app.task(name="find_new_songs")
def find_new_songs(song_id: str):
    postgres_client = SessionLocal()
    new_songs = find_new_songs_by_song_id(song_id, postgres_client)
    postgres_client.close()

    # start tasks
    for new_song in new_songs:
        celery_app.send_task("download_song", args=[new_song], queue="music", priority=4)
    return len(new_songs)

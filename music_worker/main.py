import logging

from celery import Celery

from database.postgres_database import SessionLocal
from database.redis_database import REDIS_DATABASE_URI
from task.music_task2 import download_by_song_id

logger = logging.getLogger(__name__)

celery_app = Celery(
    'main_app',
    broker=REDIS_DATABASE_URI,
    backend=REDIS_DATABASE_URI,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
    timezone='Europe/Tallinn',
)


@celery_app.task(name="music")
def music(song_id):
    postgres_client = SessionLocal()

    new_artists, new_songs = download_by_song_id(song_id, postgres_client)
    logger.info(f"a: {new_artists} | s: {new_songs}")

    postgres_client.close()
    return 3

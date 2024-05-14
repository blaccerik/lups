import logging
import time

from celery import Celery

from database.postgres_database import SessionLocal
from database.redis_database import REDIS_DATABASE_URI
from task.music_task2 import download_by_song_id2

logger = logging.getLogger(__name__)

celery_app = Celery(
    'main_app',
    broker=REDIS_DATABASE_URI,
    backend=REDIS_DATABASE_URI,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
    timezone='Europe/Tallinn',
    task_queues={
        'music': {'exchange': 'music'},
        'song': {'exchange': 'song'}
    }
)

celery_app.conf.broker_transport_options = {
    'priority_steps': list(range(10)),
    'sep': ':',
    'queue_order_strategy': 'priority',
}


@celery_app.task(name="test1")
def test1():
    time.sleep(1)
    return 1


@celery_app.task(name="test2")
def test2():
    time.sleep(1)
    return 2


@celery_app.task(name="song")
def song(song_id: str):
    time.sleep(0.1)
    return 69


@celery_app.task(name="music")
def music(song_id: str):
    time.sleep(0.1)
    return
    postgres_client = SessionLocal()
    new_artists, new_songs, new_connections = download_by_song_id2(song_id, postgres_client)
    logger.info(f"a: {len(new_artists)} | s: {len(new_songs)} | c: {new_connections}")
    postgres_client.close()

    # start tasks
    for new_song in new_songs:
        i = song.apply_async(args=[new_song], queue="music")
        print(f"{i} {new_song}")
    return


celery_app.send_task("test1", queue="music", priority=1)
celery_app.send_task("test2", queue="music", priority=2)
celery_app.send_task("test1", queue="music", priority=1)

import logging

from celery import Celery

from database.redis_database import REDIS_DATABASE_URI

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
    logger.info(song_id)
    return 3

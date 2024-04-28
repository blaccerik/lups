from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

DATABASE_URI = "redis://redis:6379/0"
celery_app = Celery(
    'main_app',
    broker=DATABASE_URI,
    backend=DATABASE_URI,
    result_expires=3600,
    timezone='Europe/Tallinn',
)

celery_app.conf.beat_schedule = {
    'get-news': {
        'task': 'news',
        'options': {'queue': 'normal'},
        # 'schedule': timedelta(seconds=5),
        'schedule': crontab(minute='19', hour='19')
    },
    # 'get-music': {
    #     'task': 'music',
    #     'options': {'queue': 'music'},
    #     'schedule': timedelta(seconds=999),
    #     # 'schedule': crontab(minute='*', hour='*')
    # },
}

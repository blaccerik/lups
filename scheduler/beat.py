import os

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
    'news': {
        'task': 'news',
        'options': {'queue': 'normal'},
        'schedule': crontab(minute='19', hour='19')
    },
    'find_new_songs': {
        'task': 'find_new_songs',
        'options': {'queue': 'music:4'},
        'schedule': crontab(minute=os.environ.get('MINUTE', '*/10'), hour=os.environ.get('HOUR', '*')),
        'args': ('',),
    },
}

import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

DATABASE_URI = os.environ.get("REDIS_BROKER_URL", 'redis://localhost:6379/0')
celery_app = Celery('my_celery_app',
                    broker=DATABASE_URI,  # Replace with your Redis server configuration
                    backend=DATABASE_URI,  # Replace with your Redis server configuration
                    )

celery_app.conf.beat_schedule = {
    'run-task': {
        'task': 'get_news',
        'schedule': crontab(hour=17,minute=25),
    },
}

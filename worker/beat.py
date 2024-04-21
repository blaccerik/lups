from celery import Celery
from celery.schedules import crontab

DATABASE_URI = "redis://redis:6379/0"
celery_app = Celery('main_app',
                    broker=DATABASE_URI,  # Replace with your Redis server configuration
                    backend=DATABASE_URI,  # Replace with your Redis server configuration
                    )

celery_app.conf.beat_schedule = {
    'run-task': {
        'task': 'news',
        'schedule': crontab(minute='25', hour='19')
    },
}
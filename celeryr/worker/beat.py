import os
from datetime import timedelta

from celery import Celery

DATABASE_URI = os.environ.get("REDIS_BROKER_URL", 'redis://localhost:6379/0')
celery_app = Celery('my_celery_app',
                    broker=DATABASE_URI,  # Replace with your Redis server configuration
                    backend=DATABASE_URI,  # Replace with your Redis server configuration
                    )

# Configure the beat schedule to run the task every 10 seconds.
celery_app.conf.beat_schedule = {
    'run-task-every-10-seconds': {
        'task': 'test',
        'schedule': timedelta(seconds=10),
    },
}

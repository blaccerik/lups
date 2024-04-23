from celery import Celery
import os

DATABASE_URI = f"redis://{os.environ.get('REDIS_BROKER_URL', 'localhost')}:6379/0"
print(DATABASE_URI)

celery_app = Celery(
    'main',
    broker=DATABASE_URI,
    backend=DATABASE_URI,
    result_expires=3600,
    timezone='Europe/Tallinn',
)

celery_app.conf.task_routes = {
    "stream": {'queue': "normal"}
}
from celery import Celery
import os

DATABASE_URI = f"redis://{os.environ.get('REDIS_BROKER_URL', 'localhost')}:6379/0"
print(DATABASE_URI)

celery_app = Celery(
    'main',
    broker=DATABASE_URI,  # Replace with your Redis server configuration
    backend=DATABASE_URI,  # Replace with your Redis server configuration
)

# Optional Celery configuration settings
celery_app.conf.update(
    result_expires=3600,  # Result expiration time in seconds (adjust as needed)
    timezone='UTC',       # Timezone for Celery tasks
)
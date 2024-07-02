import os

from celery import Celery

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

# celery_app.conf.broker_transport_options = {
#     'priority_steps': list(range(10)),
#     'sep': ':',
#     'queue_order_strategy': 'priority',
# }

# celery_app.conf.broker_transport_options = {
#     'priority_steps': list(range(10)),
#     'sep': ':',
#     'queue_order_strategy': 'priority',
# }

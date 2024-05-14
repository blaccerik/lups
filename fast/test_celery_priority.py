import time

from utils.celery_config import celery_app

if __name__ == '__main__':

    # print(celery_app.send_task("test1", queue="music:1"))
    # print(celery_app.send_task("test2", queue="music:2"))
    # print(celery_app.send_task("test1", queue="music:1"))
    # print(celery_app.send_task("test2", queue="music:2"))
    celery_app.send_task("test1", queue="music", priority=1)
    celery_app.send_task("test2", queue="music", priority=2)
    celery_app.send_task("test1", queue="music", priority=1)
    celery_app.send_task("test2", queue="music", priority=2)
    celery_app.send_task("test1", queue="music", priority=1)
    celery_app.send_task("test2", queue="music", priority=2)
    celery_app.send_task("test1", queue="music", priority=1)
    celery_app.send_task("test2", queue="music", priority=2)
    celery_app.send_task("test1", queue="music", priority=1)
    celery_app.send_task("test2", queue="music", priority=2)
    celery_app.send_task("test1", queue="music", priority=1)
    celery_app.send_task("test2", queue="music", priority=2)
    # print(celery_app.send_task("test1", queue="music", routing_key='music', priority=1))
    # print(celery_app.send_task("test2", queue="music", routing_key='music', priority=2))
    # print(celery_app.send_task("test1", queue="music", routing_key='music', priority=1))
    # print(celery_app.send_task("test2", queue="music", routing_key='music', priority=2))




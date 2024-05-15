import time

from utils.celery_config import celery_app

if __name__ == '__main__':
    print("start")
    # for i in range(10):
    #     celery_app.send_task("test1", queue="music:1")
    #     celery_app.send_task("test2", queue="music:2")

    # celery_app.send_task("test1", priority=0, queue='high_priority')
    # celery_app.send_task("test2", priority=9, queue='low_priority')

    # for i in range(5):
    #     celery_app.send_task("test2", queue="music", priority=2, routing_key='music')
    #     time.sleep(0.1)
    # celery_app.send_task("test2", queue="music", priority=2, routing_key='music')
    # celery_app.send_task("test2", queue="music:1")
    # exit()
    for i in range(5):
        result = celery_app.send_task("test1", queue="music:1")
        t1 = time.time()
        output = result.get(timeout=10)
        t2 = time.time()
        print(output, t2 - t1)
    print("------")
    for i in range(5):
        result = celery_app.send_task("test1", queue="music:2")
        t1 = time.time()
        output = result.get(timeout=10)
        t2 = time.time()
        print(output, t2 - t1)
    print("------")
    for i in range(5):
        result = celery_app.send_task("test1", queue="music:3")
        t1 = time.time()
        output = result.get(timeout=50)
        t2 = time.time()
        print(output, t2 - t1)

    # celery_app.send_task("test2", queue="music", priority=2)
    # celery_app.send_task("test1", queue="music", priority=1)
    # celery_app.send_task("test2", queue="music", priority=2)
    # celery_app.send_task("test1", queue="music", priority=1)
    # celery_app.send_task("test2", queue="music", priority=2)
    # celery_app.send_task("test1", queue="music", priority=1)
    # celery_app.send_task("test2", queue="music", priority=2)
    # celery_app.send_task("test1", queue="music", priority=1)
    # celery_app.send_task("test2", queue="music", priority=2)
    # print(celery_app.send_task("test1", queue="music", routing_key='music', priority=1))
    # print(celery_app.send_task("test2", queue="music", routing_key='music', priority=2))
    # print(celery_app.send_task("test1", queue="music", routing_key='music', priority=1))
    # print(celery_app.send_task("test2", queue="music", routing_key='music', priority=2))

import sys

from celery import Celery
from redis import Redis

from core.model import ModelLoader
from core.schemas import Message

REDIS_URI = 'redis://localhost:6379/0'
celery_app = Celery('tasks', broker=REDIS_URI, backend=REDIS_URI)

def get_redis_client():
    return Redis(host="localhost", port=6379, db=0)

@celery_app.on_after_configure.connect
def setup_model(sender, **kwargs):
    if "flower" in sys.argv:
        print("skipping model load")
        return

    # test redis connection
    redis_client = get_redis_client()
    print(redis_client.get("erik"))
    redis_client.set("erik", "tere")
    print(redis_client.get("erik"))
    redis_client.close()

    # use model
    ml = ModelLoader()
    text = ml.format_chat([
        Message(owner="user", text="What color is the sky?")
    ])
    try:
        for _ in ml.stream(text):
            continue
    except Exception as e:
        print("error")
        print(e)
        print("error")

@celery_app.task(name="test")
def add(x, y):
    return x + y

# ssh erik@134.209.198.189 -i C:\Users\erik\.ssh/id_rsa

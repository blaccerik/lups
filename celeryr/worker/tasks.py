import os
import sys
import time

from celery import Celery

from worker.chat import get_chat, format_chat
from worker.model import load_model, use_model
from worker.news import get_news

# Python 3.10.9
DATABASE_URI = os.environ.get("REDIS_BROKER_URL", 'redis://localhost:6379/0')

celery_app = Celery(
    'tasks',
    broker=DATABASE_URI,
    backend=DATABASE_URI,
)


@celery_app.on_after_configure.connect
def setup_model(sender, **kwargs):
    if "flower" in sys.argv:
        print("skipping model load")
        return
    print("start loading")
    s = time.time()
    load_model()
    e = time.time()
    print(f"models loaded: {e - s}")
    print("use model")
    s = time.time()
    res = use_model("what color is the sky")
    print(res)
    e = time.time()
    print(f"model used: {e - s}")


@celery_app.task(name="get_message", time_limit=60)
def simple_task(chat_id):
    messages = get_chat(chat_id)
    text = format_chat(messages)
    print(f"input: {[text]}")
    res = use_model(text)
    print(f"output: {[res]}")
    return res


@celery_app.task(name="get_news", time_limit=120)
def news():
    print("getting news")
    s = time.time()
    get_news()
    e = time.time()
    print(f"getting news: {e - s}")

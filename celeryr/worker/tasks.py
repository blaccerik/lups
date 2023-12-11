import json
import os
import sys
import time

import redis
from celery import Celery

from worker.chat import get_chat
from worker.model_cpp import ModelLoader
from worker.news import get_news

# Python 3.10.9
DATABASE_URI = f"redis://{os.environ.get('REDIS_BROKER_URL', 'localhost')}:6379/0"
print(DATABASE_URI)
celery_app = Celery(
    'tasks',
    broker=DATABASE_URI,
    backend=DATABASE_URI,
)


def get_client():
    return redis.Redis(host=os.environ.get('REDIS_BROKER_URL', 'localhost'), port=6379, db=0)


@celery_app.on_after_configure.connect
def setup_model(sender, **kwargs):
    if "flower" in sys.argv:
        print("skipping model load")
        return
    s = time.time()
    ml = ModelLoader()
    e = time.time()
    print(f"model loaded: {e - s}")

    s = time.time()
    text = """<|im_start|>system
A conversation between a User and Vambola. Vambola is an AI chatbot for lyps.ee. Lyps is a political party in Estonia<|im_end|>
<|im_start|>User
What color is the sky?<|im_end|>
<|im_start|>Vambola
"""
    try:
        for text_part, end in ml.stream(text):
            continue
    except Exception as e:
        print("error")
        print(e)
        print("error")
    e = time.time()
    print(f"model used: {e - s}")


@celery_app.task(name="cpp_model", bind=True)
def test(self, chat_id):
    messages = get_chat(chat_id)

    redis_client = get_client()
    updates_channel = f"task_updates:{self.request.id}"
    print(updates_channel)
    ml = ModelLoader()
    total_text = ""
    for text_part, end in ml.stream(ml.format_chat(messages)):
        if end:
            total_text = text_part
            break
        redis_client.publish(updates_channel, json.dumps({
            "text": text_part,
            "stop": False
        }))

    # stop
    redis_client.publish(updates_channel, json.dumps({
        "text": "",
        "stop": True
    }))
    redis_client.close()

    return total_text


@celery_app.task(name="get_response", time_limit=60)
def simple_task(chat_id):
    messages = get_chat(chat_id)
    ml = ModelLoader()
    text = ml.format_chat(messages)
    output_text = ml.stream(text)
    return output_text


@celery_app.task(name="get_news", time_limit=600)
def news():
    print("getting news")
    s = time.time()
    get_news()
    e = time.time()
    print(f"getting news: {e - s}")

import json
import os
import random
import sys
import time

import redis
from billiard.exceptions import SoftTimeLimitExceeded
from celery import Celery
from celery import signals
from celery.contrib.abortable import AbortableTask

from worker.chat import get_chat
from worker.database import SessionLocal, DBMessage
from worker.model_cpp import ModelLoader
from worker.news import get_news

# Python 3.10.9
DATABASE_URI = f"redis://{os.environ.get('REDIS_BROKER_URL', 'localhost')}:6379/0"
print(DATABASE_URI)
celery_app = Celery(
    'tasks',
    broker=DATABASE_URI,
    backend=DATABASE_URI
)


def get_client():
    return redis.Redis(host=os.environ.get('REDIS_BROKER_URL', 'localhost'), port=6379, db=0)


@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    print("signal asi")
    pass


@celery_app.on_after_configure.connect
def setup_model(sender, **kwargs):
    if "flower" in sys.argv:
        print("skipping model load")
        return


#     s = time.time()
#     ml = ModelLoader()
#     e = time.time()
#     print(f"model loaded: {e - s}")
#
#     s = time.time()
#     text = """<|im_start|>system
# A conversation between a User and Vambola. Vambola is an AI chatbot for lyps.ee. Lyps is a political party in Estonia<|im_end|>
# <|im_start|>User
# What color is the sky?<|im_end|>
# <|im_start|>Vambola
# """
#     try:
#         for _ in ml.stream(text):
#             continue
#     except Exception as e:
#         print("error")
#         print(e)
#         print("error")
#     e = time.time()
#     print(f"model used: {e - s}")


class PredictTask(AbortableTask):
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        # if not self.model:
        #     self.model = ModelLoader()
        return self.run(*args, **kwargs)


@celery_app.task(name="test", soft_time_limit=60, base=PredictTask, bind=True)
def test2(self, chat_id):
    messages = get_chat(chat_id)
    redis_client = get_client()
    updates_channel = f"task_updates:{chat_id}"
    try:
        for text_part in self.model.stream(self.model.format_chat(messages)):
            if self.is_aborted():
                print("aborted")
                break
            redis_client.publish(updates_channel, json.dumps({
                "text": text_part,
                "type": "message"
            }))
        redis_client.publish(updates_channel, json.dumps({
            "text": "",
            "type": "done"
        }))
    except SoftTimeLimitExceeded:
        print("time limit")
        redis_client.publish(updates_channel, json.dumps({
            "text": "",
            "type": "timeout"
        }))
    except Exception as e:
        print(e)
        redis_client.publish(updates_channel, json.dumps({
            "text": "",
            "type": "timeout"
        }))

    redis_client.close()


def loop():
    n = random.choice([50, 150])
    for i in range(n):
        yield f"t{i} "

@celery_app.task(name="stream", soft_time_limit=10, base=PredictTask, bind=True)
def stream(self, chat_id, stream_id, language):
    # database connections
    redis_client = get_client()
    postgres_client = SessionLocal()

    updates_channel = f"stream:{stream_id}"
    total_text = ""
    print("start")
    try:
        for index, text_part in enumerate(loop()):
            if self.is_aborted():
                print("aborted")
                break
            redis_client.xadd(
                updates_channel,
                {
                    "index": index,
                    "text": text_part,
                    "type": "part"
                }
            )
            total_text += text_part
            time.sleep(0.1)
    except SoftTimeLimitExceeded:
        print("time limit")
    print(total_text)
    # save full message to database
    db_output = DBMessage(
        chat_id=chat_id,
        owner="model",
        language=language,
        text=total_text,
        text_model=total_text
    )
    postgres_client.add(db_output)
    postgres_client.commit()
    message_id = db_output.id

    # send complete message to user
    redis_client.xadd(
        updates_channel,
        {
            "index": message_id,
            "text": total_text,
            "type": "end"
        }
    )
    # remove locks
    redis_client.hdel("streams", stream_id)
    redis_client.srem("chats", str(chat_id))
    redis_client.close()
    postgres_client.close()


# @celery_app.task(name="cpp_model", bind=True)
# def test(self, chat_id):
#     messages = get_chat(chat_id)
#     redis_client = get_client()
#     updates_channel = f"task_updates:{self.request.id}"
#     print(updates_channel)
#     ml = ModelLoader()
#     total_text = ""
#     for text_part, end in ml.stream(ml.format_chat(messages)):
#         if end:
#             total_text = text_part
#             break
#         print(text_part)
#         redis_client.publish(updates_channel, json.dumps({
#             "text": text_part,
#             "stop": False
#         }))
#
#     # stop
#     redis_client.publish(updates_channel, json.dumps({
#         "text": "",
#         "stop": True
#     }))
#     redis_client.close()
#
#     return total_text
#
#
# @celery_app.task(name="get_response", time_limit=60)
# def simple_task(chat_id):
#     messages = get_chat(chat_id)
#     ml = ModelLoader()
#     text = ml.format_chat(messages)
#     output_text = ml.stream(text)
#     return output_text


@celery_app.task(name="get_news", time_limit=600)
def news():
    print("getting news")
    s = time.time()
    get_news()
    e = time.time()
    print(f"getting news: {e - s}")

import sys
import time

from billiard.exceptions import SoftTimeLimitExceeded
from celery import Celery
from redis import Redis

from core.model import ModelLoader
from core.predict_task import PredictTask
from core.schemas import Message

REDIS_URI = 'redis://localhost:6379/0'
celery_app = Celery('tasks', broker=REDIS_URI, backend=REDIS_URI)
MAX_TEXT_LEN = 1024
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

@celery_app.task(name="test", soft_time_limit=60, base=PredictTask, bind=True)
def add(self, text, stream_id):
    total_text = ""
    redis_client = get_redis_client()
    updates_channel = f"stream:{stream_id}"
    messages = [
        Message(owner="user", text=text)
    ]
    try:
        # for index, text_part in enumerate(loop()):
        for index, text_part in enumerate(self.cpp_model.stream(self.cpp_model.format_chat(messages))):
            if self.is_aborted():
                print("aborted")
                break
            elif len(total_text) + len(text_part) >= MAX_TEXT_LEN:
                print("too long")
                break
            total_text += text_part
            redis_client.xadd(
                updates_channel,
                {
                    "index": index,
                    "text": total_text,
                    "type": "part"
                }
            )
            time.sleep(0.05)
    except SoftTimeLimitExceeded:
        print("time limit")
    message_id = -1
    redis_client.xadd(
        updates_channel,
        {
            "index": message_id,
            "text": total_text,
            "type": "end"
        }
    )
    redis_client.close()
    return

# ssh erik@134.209.198.189 -i C:\Users\erik\.ssh/id_rsa

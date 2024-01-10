import uuid

from celery import Celery
from redis import Redis

url = "redis://10.0.0.2:6379/0"
# url = "redis://134.209.198.189:6379/0"
app = Celery(
    'tasks',
    broker=url,
    backend=url
)

def get_redis_client():
    return Redis(host="10.0.0.2", port=6379, db=0, decode_responses=True)

if __name__ == '__main__':

    question = "how to i make a bomb?"

    stream_id = uuid.uuid4().hex
    result = app.send_task('test', (question, stream_id))

    # prepare for stream
    redis_client = get_redis_client()
    updates_channel = f"stream:{stream_id}"
    last_redis_id = 0
    max_wait_time = 240_000
    wait_time = 100
    n = max_wait_time // wait_time
    for _ in range(n):
        redis_stream_message = redis_client.xread(streams={updates_channel: last_redis_id},
                                                  count=1,
                                                  block=wait_time)
        if len(redis_stream_message) == 0:
            continue

        # load message
        last_redis_id, raw_data = redis_stream_message[0][1][0]
        text_part = raw_data["text"]
        text_index = int(raw_data["index"])
        task_type = raw_data["type"]
        print(text_part)

        # end loop
        if task_type == "end":
            break
    redis_client.close()
    # print(result.get())
import time

from billiard.exceptions import SoftTimeLimitExceeded
from celery import Celery

from database.models import DBMessage
from database.postgres_database import SessionLocal
from database.redis_database import get_client
from services.chat import get_chat_messages
from task.predict_task import PredictTask

# Python 3.11.8
DATABASE_URI = "redis://redis:6379/0"
celery_app = Celery(
    'main',
    broker=DATABASE_URI,
    backend=DATABASE_URI,
    broker_connection_retry_on_startup=True
)
MAX_TEXT_LEN = 512


@celery_app.task(name="stream", soft_time_limit=60, base=PredictTask, bind=True)
def stream(self, chat_id, stream_id, language):
    # get db
    redis_client = get_client()
    postgres_client = SessionLocal()

    messages = get_chat_messages(chat_id, postgres_client)
    print(messages)

    text = self.cpp_model.format_chat(messages)
    total_text = ""
    updates_channel = f"stream:{stream_id}"
    t1 = time.time()
    try:
        for index, text_part in enumerate(self.cpp_model.stream(text)):
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
    t2 = time.time()
    print(f"Total text:\n{total_text}")
    print(f"Time taken: {t2 - t1}")

    db_output = DBMessage(
        chat_id=chat_id,
        owner="model",
        language=language,
        text=total_text,
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

    # free locks
    redis_client.hdel("streams", stream_id)
    redis_client.srem("chats", str(chat_id))

    redis_client.close()
    postgres_client.close()

    # messages = get_chat(chat_id, postgres_client)
    # updates_channel = f"stream:{stream_id}"
    # total_text = ""
    # print("start")
    # try:
    #     # for index, text_part in enumerate(loop()):
    #     for index, text_part in enumerate(self.cpp_model.stream(self.cpp_model.format_chat(messages))):
    #         if self.is_aborted():
    #             print("aborted")
    #             break
    #         elif len(total_text) + len(text_part) >= MAX_TEXT_LEN:
    #             print("too long")
    #             break
    #         total_text += text_part
    #         redis_client.xadd(
    #             updates_channel,
    #             {
    #                 "index": index,
    #                 "text": total_text,
    #                 "type": "part"
    #             }
    #         )
    #
    #         time.sleep(0.1)
    # except SoftTimeLimitExceeded:
    #     print("time limit")
    # # save full message to database
    # db_output = DBMessage(
    #     chat_id=chat_id,
    #     owner="model",
    #     language=language,
    #     text=total_text,
    #     text_model=total_text
    # )
    # try:
    #     postgres_client.add(db_output)
    #     postgres_client.commit()
    #     message_id = db_output.id
    #     # send complete message to user
    #     redis_client.xadd(
    #         updates_channel,
    #         {
    #             "index": message_id,
    #             "text": total_text,
    #             "type": "end"
    #         }
    #     )
    # except Exception as e:
    #     print("DB ERROR")
    #     print(e)
    #     print("DB ERROR")
    # finally:
    #     # remove locks
    #     redis_client.hdel("streams", stream_id)
    #     redis_client.srem("chats", str(chat_id))
    #     redis_client.close()
    #     postgres_client.close()

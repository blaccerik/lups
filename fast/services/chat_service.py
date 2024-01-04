import json
import logging

from deep_translator import GoogleTranslator
from fastapi import HTTPException
from redis import Redis
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.models import DBUser, DBChat, DBMessage
from utils.schemas import User, MessageOwner, Message, LanguageType, ChatPost, ChatRespond

MAX_USER_TEXT_SIZE = 100
MAX_MODEL_TEXT_SIZE = 512
MAX_USER_NAME_SIZE = 50

logger = logging.getLogger("ChatService")


def read_user(user: User, session: Session):
    dbuser = session.query(DBUser).filter_by(google_id=user.google_id).first()
    if dbuser is None:
        if len(user.name) >= MAX_USER_NAME_SIZE:
            name = user.name[:MAX_USER_NAME_SIZE]
        else:
            name = user.name
        dbuser = DBUser()
        dbuser.name = name
        dbuser.google_id = user.google_id
        session.add(dbuser)
        session.commit()
        return dbuser.id
    return dbuser.id


def create_chat(user_id: int, session: Session) -> ChatRespond:
    c = DBChat()
    c.user_id = user_id
    session.add(c)
    session.flush()
    c.title = f"Chat {c.id}"
    session.commit()
    return ChatRespond(chat_id=c.id, title=c.title)


async def user_has_chat(chat_id: int, user_id: int, session: Session):
    chat = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.id == chat_id,
        DBChat.deleted == False
    )).first()
    if chat is None:
        raise HTTPException(status_code=403, detail="User does not have the chat")
    return chat

async def update_chat_title(title: str, chat_id: int, user_id: int, session: Session):
    if len(title) > 100:
        raise HTTPException(status_code=400, detail="Title too long")
    chat = await user_has_chat(chat_id, user_id, session)
    chat.title = title
    session.add(chat)
    session.commit()


def read_chats_by_user(user_id: int, session: Session) -> list:
    chats = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.deleted == False,
    )).all()
    if len(chats) == 0:
        chat_respond = create_chat(user_id, session)
        return [chat_respond]
    return [ChatRespond(title=c.title, chat_id=c.id) for c in chats]


def read_messages(chat_id: int, user_id: int, session: Session):
    # check if user has that chat
    chat = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.id == chat_id,
        DBChat.deleted == False
    )).first()
    if chat is None:
        raise HTTPException(status_code=403, detail="User does not have the chat")
    messages = session.query(DBMessage).filter(and_(
        DBMessage.chat_id == chat_id,
        DBMessage.deleted == False
    )).all()
    return [Message(
        message_id=dbm.id,
        message_text=dbm.text,
        message_owner=MessageOwner(dbm.owner),
        language_type=LanguageType(dbm.language)
    ) for dbm in messages]


def delete_messages(chat_id: int, user_id: int, session: Session):
    # check if user has that chat
    chat = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.id == chat_id,
        DBChat.deleted == False
    )).first()
    if chat is None:
        return
    messages = session.query(DBMessage).filter(and_(
        DBMessage.chat_id == chat.id,
        DBMessage.deleted == False
    )).all()
    for m in messages:
        m.deleted = True
        session.add(m)
    session.commit()


def create_message(chat_id: int, chat_post: ChatPost, postgres_client: Session) -> int:
    # validate input
    if len(chat_post.message_text) > MAX_USER_TEXT_SIZE:
        raise HTTPException(status_code=400, detail="Text too long")

    # translate
    input_text = chat_post.message_text
    input_text_model = chat_post.message_text

    # write input to database
    db_input = DBMessage(
        chat_id=chat_id,
        owner="user",
        language=chat_post.language_type.value,
        text=input_text,
        text_model=input_text_model
    )
    postgres_client.add(db_input)
    postgres_client.commit()
    return db_input.id


def translate(source: str, dest: str, text: str):
    try:
        return GoogleTranslator(source=source, target=dest).translate(text)
    except:
        return text


async def task_stream(
        stream_id: str,
        redis_client: Redis,
):
    # prepare for stream
    updates_channel = f"stream:{stream_id}"
    last_redis_id = 0
    max_wait_time = 240_000
    wait_time = 100
    n = max_wait_time // wait_time
    for _ in range(n):
        # read message
        redis_stream_message = await redis_client.xread(streams={updates_channel: last_redis_id}, count=1,
                                                        block=wait_time)
        if len(redis_stream_message) == 0:
            continue

        # load message
        last_redis_id, raw_data = redis_stream_message[0][1][0]
        text_part = raw_data["text"]
        text_index = int(raw_data["index"])
        task_type = raw_data["type"]
        logger.info(f"Data: {task_type} {text_index} size: {len(text_part)}")
        yield {
            "event": "message",
            "id": text_index,
            "retry": 1000,
            "data": json.dumps({
                "text": text_part,
                "type": task_type,
                "id": text_index
            })
        }

        # end loop
        if task_type == "end":
            break

    else:
        # end loop if it goes on for too long
        logger.error("Took to long to get messages")

    logger.info("------------CLEAN UP------------")
    s = await redis_client.hget("streams", stream_id)
    c = await redis_client.smembers("chats")
    logger.info(f"chats: {c} streams: {s}")
    logger.info("------------CLEAN UP------------")

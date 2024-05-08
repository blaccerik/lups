import json
import logging
from typing import List

from deep_translator import GoogleTranslator
from fastapi import HTTPException
from redis import Redis
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBUser, DBChat, DBMessage
from schemas.chat import Chat, ChatMessage, LanguageType, OwnerType
from schemas.auth import User

MAX_USER_NAME_SIZE = 50

logger = logging.getLogger("ChatService")


def read_user(user: User, session: Session):
    print(user)
    dbuser = session.query(DBUser).filter_by(google_id=user.google_id).first()
    print(dbuser)
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


def create_chat(user_id: int, session: Session) -> Chat:
    c = DBChat()
    c.user_id = user_id
    session.add(c)
    session.flush()
    c.title = f"Chat {c.id}"
    session.commit()
    return Chat(chat_id=c.id, title=c.title)


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
    chat = await user_has_chat(chat_id, user_id, session)
    chat.title = title
    session.add(chat)
    session.commit()


def read_chats_by_user(user_id: int, session: Session) -> List[Chat]:
    chats = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.deleted == False,
    )).all()
    if len(chats) == 0:
        chat_respond = create_chat(user_id, session)
        return [chat_respond]
    return [Chat(title=c.title, chat_id=c.id) for c in chats]


async def read_messages(chat_id: int, user_id: int, session: Session) -> List[ChatMessage]:
    await user_has_chat(chat_id, user_id, session)
    messages = session.query(DBMessage).filter(and_(
        DBMessage.chat_id == chat_id,
        DBMessage.deleted == False
    )).order_by(DBMessage.id).all()
    return [ChatMessage(
        id=dbm.id,
        text=dbm.text,
        owner=OwnerType(dbm.owner),
        language=LanguageType(dbm.language)
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


def create_message(chat_id: int, chat_message: ChatMessage, postgres_client: Session) -> int:
    # todo translate step

    # write user input to database
    db_user_msg = DBMessage(
        chat_id=chat_id,
        owner="user",
        language=chat_message.language.value,
        text=chat_message.text,
    )
    postgres_client.add(db_user_msg)
    postgres_client.commit()
    return db_user_msg.id


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
        redis_stream_message = await redis_client.xread(streams={updates_channel: last_redis_id},
                                                        count=1,
                                                        block=wait_time)
        # no new message
        if len(redis_stream_message) == 0:
            continue

        # load message
        last_redis_id, raw_data = redis_stream_message[0][1][0]
        text_part = raw_data["text"]
        text_index = int(raw_data["index"])
        task_type = raw_data["type"]

        # log
        if task_type == "part" and text_index % 10 == 0:
            logger.info(f"Data: {task_type} {text_index} size: {len(text_part)}")
        elif task_type == "end":
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

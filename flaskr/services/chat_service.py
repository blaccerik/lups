import os
import time

from celery import Celery
from celery.result import AsyncResult
from deep_translator import GoogleTranslator
from flask import abort
from sqlalchemy import and_

from db_models.models import User, Chat, Message, with_session
from shared import logger

celery = Celery("tasks")
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

MAX_USER_TEXT_SIZE = 100
MAX_USER_NAME_SIZE = 50


@with_session
def get_user(name: str, google_id: int, session=None) -> int:
    user = session.query(User).filter_by(google_id=google_id).first()
    if user is None:

        if len(name) >= MAX_USER_NAME_SIZE:
            name = name[:MAX_USER_NAME_SIZE]

        u = User()
        u.name = name
        u.google_id = google_id
        session.add(u)
        session.commit()
        return u.id
    return user.id


@with_session
def create_chat(user_id: int, session=None) -> int:
    c = Chat()
    c.user_id = user_id
    session.add(c)
    session.commit()
    return c.id


@with_session
def get_chats(user_id: int, session=None) -> list:
    chats = session.query(Chat).filter(and_(
        Chat.user_id == user_id,
        Chat.deleted == False,
    )).all()
    if len(chats) == 0:
        chat_id = create_chat(user_id)
        return [chat_id]
    return [c.id for c in chats]


@with_session
def get_chat(user_id: int, code: int, session=None) -> list:
    # check if user has that chat
    chat = session.query(Chat).filter(and_(
        Chat.user_id == user_id,
        Chat.id == code,
        Chat.deleted == False
    )).first()
    if chat is None:
        abort(403, "User does not have the chat")
    messages = session.query(Message).filter(and_(
        Message.chat_id == code,
        Message.deleted == False
    )).all()
    return [{"id": m.id, "message": m.message_ee, "type": m.type} for m in messages]


@with_session
def clear(user_id: int, code: int, session=None):
    # check if user has that chat
    chat = session.query(Chat).filter(and_(
        Chat.user_id == user_id,
        Chat.id == code,
        Chat.deleted == False
    )).first()
    if chat is None:
        abort(403, "User does not have the chat")
    messages = session.query(Message).filter(and_(
        Message.chat_id == chat.id,
        Message.deleted == False
    )).all()
    logger.info(f"before del: {len(messages)}")
    for m in messages:
        m.deleted = True
        session.add(m)
    session.commit()
    messages = session.query(Message).filter(and_(
        Message.chat_id == chat.id,
        Message.deleted == False
    )).all()
    logger.info(f"after del: {len(messages)}")


@with_session
def post_message(user_id: int, code: int, text_ee: str, session=None):
    # check if user has that chat
    chat = session.query(Chat).filter(and_(
        Chat.user_id == user_id,
        Chat.id == code,
        Chat.deleted == False
    )).first()
    if chat is None:
        abort(403, "User does not have the chat")

    # check text
    if len(text_ee) >= MAX_USER_TEXT_SIZE:
        abort(400, "Too long text")

    # translate
    logger.info(f"ee in: {text_ee}")
    try:
        text_en = GoogleTranslator(source='et', target='en').translate(text_ee)
    except:
        text_en = text_ee

    # check text
    if text_en is None:
        text_en = ""
    elif len(text_en) >= MAX_USER_TEXT_SIZE:
        abort(400, "Too long text")
    logger.info(f"en in: {text_en}")

    m = Message()
    m.chat_id = chat.id
    m.type = "user"
    m.message_ee = text_ee
    m.message_en = text_en
    session.add(m)
    session.commit()

    task = celery.send_task("my_task", args=[chat.id, m.id])
    try:
        okay, output_en = task.get()
    except Exception as e:
        logger.exception(e)
        abort(400, "Server busy")
        return
    if not okay:
        logger.exception(output_en)
        abort(400, "Celery error")
    logger.info(f"en out: {output_en}")

    if len(output_en) >= MAX_USER_TEXT_SIZE:
        output_en = output_en[:MAX_USER_TEXT_SIZE]

    try:
        output_ee = GoogleTranslator(source='en', target='et').translate(output_en)
    except:
        output_ee = output_en
    logger.info(f"ee out: {output_ee}")

    if len(output_ee) >= MAX_USER_TEXT_SIZE:
        output_ee = output_ee[:MAX_USER_TEXT_SIZE]

    m = Message()
    m.chat_id = chat.id
    m.type = "bot"
    m.message_ee = output_ee
    m.message_en = output_en
    session.add(m)
    session.commit()
    return {"id": m.id, "message": output_ee, "type": m.type}


def stream():
    task = celery.send_task("stream_chat")
    while task.state == "PENDING":
        print(task.info)
    print(task.state)
    print(task.info)
    print("start")
    a = task.get()
    print(a)

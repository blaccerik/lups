from deep_translator import GoogleTranslator
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.models import DBUser, DBChat, DBMessage
from utils.celery_config import celery_app
from utils.schemas import User, Message, MessageType

MAX_USER_TEXT_SIZE = 100
MAX_USER_NAME_SIZE = 50


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


def create_chat(user_id: int, session=None) -> int:
    c = DBChat()
    c.user_id = user_id
    session.add(c)
    session.commit()
    return c.id


def read_chats_by_user(user_id: int, session: Session):
    chats = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.deleted == False,
    )).all()
    if len(chats) == 0:
        chat_id = create_chat(user_id, session)
        return [chat_id]
    return [c.id for c in chats]


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
    return [Message(id=dbm.id, message=dbm.message_ee, type=MessageType(dbm.type)) for dbm in messages]



def create_message(text_ee: str, chat_id: int, user_id: int, session: Session):
    # check if user has that chat
    chat = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.id == chat_id,
        DBChat.deleted == False
    )).first()
    if chat is None:
        raise HTTPException(status_code=403, detail="User does not have the chat")

    # check text
    if len(text_ee) >= MAX_USER_TEXT_SIZE:
        raise HTTPException(status_code=400, detail="Too long text")

    # translate
    try:
        text_en = GoogleTranslator(source='et', target='en').translate(text_ee)
    except:
        text_en = text_ee

    # check text
    if text_en is None:
        text_en = ""
    elif len(text_en) >= MAX_USER_TEXT_SIZE:
        raise HTTPException(status_code=400, detail="Too long text")

    m = DBMessage()
    m.chat_id = chat.id
    m.type = "user"
    m.message_ee = text_ee
    m.message_en = text_en
    session.add(m)
    session.commit()

    task = celery_app.send_task("get_response", args=[chat.id])
    print(task)

    try:
        output_en = task.get()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Server busy")
    if not output_en:
        raise HTTPException(status_code=400, detail="Celery error")
    print(output_en)
    if len(output_en) >= MAX_USER_TEXT_SIZE:
        output_en = output_en[:MAX_USER_TEXT_SIZE]

    try:
        output_ee = GoogleTranslator(source='en', target='et').translate(output_en)
    except:
        output_ee = output_en

    if len(output_ee) >= MAX_USER_TEXT_SIZE:
        output_ee = output_ee[:MAX_USER_TEXT_SIZE]

    m = DBMessage()
    m.chat_id = chat.id
    m.type = "bot"
    m.message_ee = output_ee
    m.message_en = output_en
    session.add(m)
    session.commit()
    return Message(id=m.id, message=output_ee, type=MessageType(m.type))


def delete_messages(chat_id: int, user_id: int, session: Session):
    # check if user has that chat
    chat = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.id == chat_id,
        DBChat.deleted == False
    )).first()
    if chat is None:
        raise HTTPException(status_code=403, detail="User does not have the chat")
    messages = session.query(DBMessage).filter(and_(
        DBMessage.chat_id == chat.id,
        DBMessage.deleted == False
    )).all()
    for m in messages:
        m.deleted = True
        session.add(m)
    session.commit()

import asyncio
import json
from asyncio import CancelledError

from deep_translator import GoogleTranslator
from fastapi import HTTPException
from redis import Redis
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket

from models.models import DBUser, DBChat, DBMessage
from utils.celery_config import celery_app
from utils.schemas import User, MessageSend, MessageOwner, Message, ChatInput, ChatOutputMessage, \
    OutputType, LanguageType, ChatOutputError

MAX_USER_TEXT_SIZE = 100
MAX_MODEL_TEXT_SIZE = 512
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


async def read_chat(chat_id: int, user_id: int, session: Session) -> bool:
    chat = session.query(DBChat).filter(and_(
        DBChat.user_id == user_id,
        DBChat.id == chat_id,
        DBChat.deleted == False
    )).first()
    return chat is not None


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
    return [Message(
        message_id=dbm.id,
        message_text=dbm.text,
        message_owner=MessageOwner(dbm.owner),
        language_type=LanguageType(dbm.language)
    ) for dbm in messages]


def delete_messages(chat_id: int, user_id: int, session: Session):
    print("deleted")
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


def translate(source: str, dest: str, text: str):
    try:
        return GoogleTranslator(source=source, target=dest).translate(text)
    except:
        return text

async def process_input_and_send(chat_id: int,
                                 user_id: int,
                                 chat_input: ChatInput,
                                 websocket: WebSocket,
                                 postgres_client: Session,
                                 redis_client: Redis):
    output_text = ""
    output_text_model = ""
    try:
        # check message
        if len(chat_input.message_text) > MAX_USER_TEXT_SIZE:
            await redis_client.srem("chats", str(chat_id))
            await websocket.send_text(ChatOutputError(type=OutputType.error, message_text="Text is too long").model_dump_json())
            return

        # translate if needed
        if chat_input.language_type == LanguageType.estonia:

            # translate
            message_text_en = translate("et", "en", chat_input.message_text)
            if len(message_text_en) > MAX_USER_TEXT_SIZE:
                await redis_client.srem("chats", str(chat_id))
                await websocket.send_text(ChatOutputError(type=OutputType.error, message_text="Text is too long").model_dump_json())
                return
            input_text = chat_input.message_text
            input_text_model = message_text_en
        else:
            input_text = chat_input.message_text
            input_text_model = chat_input.message_text

        # write input to database
        db_input = DBMessage(
            chat_id=chat_id,
            owner="user",
            language=chat_input.language_type.value,
            text=input_text,
            text_model=input_text_model
        )
        postgres_client.add(db_input)
        postgres_client.commit()

        # stream loop
        async for count, output_text_part in process_input(chat_id, redis_client, chat_input.language_type):
            output_text_model += output_text_part
            # translate
            if chat_input.language_type == LanguageType.estonia:
                output_text = translate("en", "et", output_text_model)
            else:
                output_text = output_text_model
            # too long text
            if len(output_text) >= MAX_MODEL_TEXT_SIZE:
                output_text = output_text[:MAX_MODEL_TEXT_SIZE]
            if len(output_text_model) >= MAX_MODEL_TEXT_SIZE:
                output_text_model = output_text_model[:MAX_MODEL_TEXT_SIZE]

            # stream to user
            await websocket.send_text(ChatOutputMessage(
                type=OutputType.stream_message,
                message_id=count,
                message_text=output_text,
                message_owner=MessageOwner.model,
                language_type=LanguageType.english,
            ).model_dump_json())
        # write output to database
        db_output = DBMessage(
            chat_id=chat_id,
            owner="model",
            language=chat_input.language_type.value,
            text=output_text,
            text_model=output_text_model
        )
        postgres_client.add(db_output)
        postgres_client.commit()
        await redis_client.srem("chats", str(chat_id))
    except CancelledError as c:
        # cancel + delete request
        if str(c) == "delete":
            delete_messages(chat_id, user_id, postgres_client)
        # write half message to db
        elif output_text != "" and output_text_model != "":
            db_output = DBMessage(
                chat_id=chat_id,
                owner="model",
                language=chat_input.language_type.value,
                text=output_text,
                text_model=output_text_model
            )
            postgres_client.add(db_output)
            postgres_client.commit()
        await redis_client.srem("chats", str(chat_id))
    except Exception as e:
        print("error")
        print(e)
        print("error")
        await redis_client.srem("chats", str(chat_id))


async def process_input(chat_id: int, redis_client: Redis, language_type: LanguageType):

    should_buffer = language_type == LanguageType.estonia
    buffer_size = 5

    # send task
    task = celery_app.send_task("cpp_model", args=[chat_id])
    # start listening to task
    updates_channel = f"task_updates:{task.id}"
    channel = redis_client.pubsub()
    await channel.subscribe(updates_channel)
    count = 0
    if should_buffer:
        buffer = []
        while True:
            message = await channel.get_message()
            if not message:
                await asyncio.sleep(0.5)
                continue
            if message["type"] != "message":
                continue
            count += 1
            data = json.loads(message["data"])
            if data["stop"]:
                break
            buffer.append(data["text"])
            if len(buffer) >= buffer_size:
                yield count, "".join(buffer)
                buffer = []
        if len(buffer) > 0:
            yield count, "".join(buffer)
    else:
        async for message in channel.listen():
            if message["type"] != "message":
                continue
            count += 1
            data = json.loads(message["data"])
            if data["stop"]:
                break
            yield count, data["text"]
    # delete channel
    await channel.unsubscribe()
    # finish task
    total_text = task.get()

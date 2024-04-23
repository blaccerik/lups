import json
import logging
import uuid

from celery.contrib.abortable import AbortableAsyncResult
from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from sqlalchemy.orm import Session
from sse_starlette import EventSourceResponse

from schemas.chat import ChatUpdate, ChatPostRespond, ChatMessage, OwnerType
from services.chat_service import read_user, read_chats_by_user, read_messages, user_has_chat, create_chat, task_stream, \
    create_message, update_chat_title
from utils.auth import get_current_user
from utils.celery_config import celery_app
from database.postgres_database import get_postgres_db
from database.redis_database import get_redis_database
from schemas.schemas import User

router = APIRouter(prefix="/api/chat")
logger = logging.getLogger("Chat")


@router.get("/")
async def get_chats(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_postgres_db)
):
    user_id = read_user(current_user, db)
    chats = read_chats_by_user(user_id, db)
    return chats


@router.get("/new")
async def get_chat(
        current_user: User = Depends(get_current_user),
        postgres_client: Session = Depends(get_postgres_db)
):
    user_id = read_user(current_user, postgres_client)
    chat_response = create_chat(user_id, postgres_client)
    return chat_response


@router.get("/{chat_id}")
async def get_chat_by_id(
        chat_id: int,
        current_user: User = Depends(get_current_user),
        postgres_client: Session = Depends(get_postgres_db)
):
    user_id = read_user(current_user, postgres_client)
    return await read_messages(chat_id, user_id, postgres_client)


@router.put("/{chat_id}")
async def update_chat(
        chat_id: int,
        chat_update: ChatUpdate,
        current_user: User = Depends(get_current_user),
        postgres_client: Session = Depends(get_postgres_db)
):
    user_id = read_user(current_user, postgres_client)

    await update_chat_title(chat_update.title, chat_id, user_id, postgres_client)

    return


@router.post("/{chat_id}")
async def post_chat_by_id(
        chat_id: int,
        chat_message: ChatMessage,
        current_user: User = Depends(get_current_user),
        redis_client: Redis = Depends(get_redis_database),
        postgres_client: Session = Depends(get_postgres_db)
):
    # check if chat is not in queue
    if await redis_client.sismember("chats", str(chat_id)):
        raise HTTPException(status_code=403, detail="Chat is in queue")

    # verify request
    if chat_message.owner.value == OwnerType.user.value:
        raise HTTPException(status_code=403, detail="Model is required")

    # check if user has chat
    user_id = read_user(current_user, postgres_client)
    await user_has_chat(chat_id, user_id, postgres_client)

    # add message to database
    dbm_id = create_message(chat_id, chat_message, postgres_client)

    # lock chat
    await redis_client.sadd("chats", str(chat_id))

    # send task to worker
    stream_id = uuid.uuid4().hex
    task = celery_app.send_task("stream", queue="normal", args=[
        chat_id,
        stream_id,
        chat_message.language.value,
        chat_message.owner.value
    ])

    # save stream
    await redis_client.hset("streams", stream_id, json.dumps({
        "task": task.id
    }))
    return ChatPostRespond(stream_id=stream_id, message_id=dbm_id)


@router.delete("/stream/{stream_id}")
async def delete_chat_stream(
        stream_id: str,
        redis_client: Redis = Depends(get_redis_database)
):
    # check if stream exists
    raw_data = await redis_client.hget("streams", stream_id)
    if raw_data is None:
        raise HTTPException(status_code=403, detail="Stream does not exist")
    data = json.loads(raw_data)
    task_id = data["task"]
    a = AbortableAsyncResult(task_id)
    r = a.abort()
    logger.info(f"Aborted {task_id} {r}")
    return


@router.get("/stream/{stream_id}")
async def get_chat_stream(
        stream_id: str,
        redis_client: Redis = Depends(get_redis_database)
):
    # check if stream exists
    raw_data = await redis_client.hget("streams", stream_id)
    if raw_data is None:
        raise HTTPException(status_code=403, detail="Stream does not exist")

    # start loop
    return EventSourceResponse(task_stream(stream_id, redis_client))

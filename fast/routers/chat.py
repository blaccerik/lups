import asyncio
import json
import json
import logging
from asyncio import create_task, Task

from fastapi import APIRouter, Depends
from pydantic import ValidationError
from redis import Redis
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket

from services.chat_service import read_user, read_chats_by_user, read_messages, delete_messages, \
    read_chat, process_input_and_send
from utils.auth import get_current_user, get_current_user_with_token
from utils.database import get_db
from utils.redis_database import get_redis
from utils.schemas import User, ChatInput, ChatOutputData, OutputType, ChatOutputError, InputType, ChatOutput

router = APIRouter(prefix="/api/chat")
logger = logging.getLogger("Chat")


@router.get("/")
async def get_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = read_user(current_user, db)
    chats = read_chats_by_user(user_id, db)
    return chats


@router.get("/{chat_id}")
async def get_chat(chat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = read_user(current_user, db)
    return read_messages(chat_id, user_id, db)


@router.websocket("/{chat_id}")
async def websocket_endpoint(
        chat_id: int,
        authorization: str,
        websocket: WebSocket,
        redis_client: Redis = Depends(get_redis),
        postgres_client: Session = Depends(get_db)
):
    await websocket.accept()

    # verify user
    try:
        user = await get_current_user_with_token(authorization)
    except:
        await websocket.close()
        return
    if user is None:
        await websocket.close()
        return

    user_id = read_user(user, postgres_client)

    # verify chat
    has_chat = await read_chat(chat_id, user_id, postgres_client)
    if not has_chat:
        await websocket.close()
        return

    # send data about queue / models
    await websocket.send_text(ChatOutputData(queue_number=0, type=OutputType.data).model_dump_json())

    # main loop
    current_task: Task | None = None
    try:
        while True:
            chat_input = ChatInput(**json.loads(await websocket.receive_text()))
            logger.info(user)
            logger.info(chat_input)

            # cancel
            if chat_input.type == InputType.cancel:
                cancel_task(-1, -1, None, current_task, False)
                current_task = None
                await websocket.send_text(ChatOutput(type=OutputType.completed).model_dump_json())
            # delete
            elif chat_input.type == InputType.delete:
                cancel_task(chat_id, user_id, postgres_client, current_task, True)
                current_task = None
                await websocket.send_text(ChatOutput(type=OutputType.completed).model_dump_json())
            # stream
            elif chat_input.type == InputType.message:
                current_task = await process_message(chat_id, user_id, chat_input, current_task, redis_client,
                                                     postgres_client, websocket)
    except ValidationError as v:
        print(v)
        await websocket.send_text(ChatOutputError(type=OutputType.error, message_text="Bad input").model_dump_json())
        await websocket.close()
    except Exception as e:
        print("main loop error")
        print(e)
        print("main loop error")
    finally:
        # end stream if user disconnects
        cancel_task(-1, -1, None, current_task, False)


def cancel_task(chat_id: int, user_id: int, postgres_client: Session, current_task: Task | None, delete: bool):
    # cancel message
    if not delete:
        if current_task:
            current_task.cancel()
        return
    # delete message
    if current_task:
        successful = current_task.cancel("delete")
        if not successful:
            delete_messages(chat_id, user_id, postgres_client)
    else:
        delete_messages(chat_id, user_id, postgres_client)


async def process_message(
        chat_id: int,
        user_id: int,
        chat_input: ChatInput,
        current_task: Task | None,
        redis_client: Redis,
        postgres_client: Session,
        websocket: WebSocket
):
    # check for previous jobs
    if await redis_client.sismember("chats", str(chat_id)):
        await websocket.send_text(
            ChatOutputError(type=OutputType.error, message_text="Already in queue").model_dump_json())
        return current_task
    # run task
    await redis_client.sadd("chats", str(chat_id))
    return create_task(process_input_and_send(chat_id, user_id, chat_input, websocket, postgres_client, redis_client))

import asyncio
import logging
import random
from typing import List

from fastapi import APIRouter, Depends, WebSocket, Path, Body
from pydantic import ValidationError
from sqlalchemy.orm import Session

from schemas.familyfeud import Answer, GameRoundData, GameRound, Code
from services.chat_service import read_user
from services.games.family import read_games_by_user, create_game_by_user, read_game, create_game_data, \
    start_game_by_user
from utils.auth import get_current_user
from utils.database import get_db
from utils.schemas import User

router = APIRouter(prefix="/api/familyfeud")
connected_clients = []

logger = logging.getLogger("Family")


@router.get("/games")
async def get_token(
        user: User = Depends(get_current_user),
        postgres_client: Session = Depends(get_db)
):
    user_id = read_user(user, postgres_client)
    return read_games_by_user(user_id, postgres_client)


@router.post("/create")
async def create_game(
        user: User = Depends(get_current_user),
        postgres_client: Session = Depends(get_db),
):
    user_id = read_user(user, postgres_client)
    return create_game_by_user(user_id, postgres_client)


@router.get("/games/{code}")
async def get_game_data(
        code: str,
        user: User = Depends(get_current_user),
        postgres_client: Session = Depends(get_db)
):
    user_id = read_user(user, postgres_client)
    return read_game(code, user_id, postgres_client)


@router.post("/games/{code}")
async def post_data(
        code: str = Path(min_length=4, max_length=4),
        data: List[GameRound] = Body(),
        user: User = Depends(get_current_user),
        postgres_client: Session = Depends(get_db)
):
    print("Received code:", code)
    print("Received data:", data)
    user_id = read_user(user, postgres_client)
    create_game_data(code, data, user_id, postgres_client)
    return read_game(code, user_id, postgres_client)


@router.post("/games/{code}/start")
async def start_game(
        code: str,
        user: User = Depends(get_current_user),
        postgres_client: Session = Depends(get_db),
):
    user_id = read_user(user, postgres_client)
    return start_game_by_user(code, user_id, postgres_client)


@router.websocket("/ws/{code}")
async def websocket_endpoint(
        code: str,
        websocket: WebSocket,
        auth: str | None = None,
):
    await websocket.accept()
    print(code, auth)
    await asyncio.sleep(1)
    try:
        while True:
            data = GameRoundData(current=random.randrange(4, 12), total=random.randrange(4, 12), questions=[
                Answer(text="tere", points=3),
                Answer(text="tere", points=33),
                Answer(text="tere", points=32),
                Answer(text="tere", points=322),
            ])
            await websocket.send_text(data.model_dump_json())
            await asyncio.sleep(3)
    except (ValidationError or ValueError) as ve:
        logger.error(ve)
        await websocket.close()
    except Exception as e:
        logger.error(e)
    finally:
        pass

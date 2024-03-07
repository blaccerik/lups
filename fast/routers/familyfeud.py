import json
import logging
from typing import List

from fastapi import APIRouter, Depends, WebSocket, Path, Body
from pydantic import ValidationError
from redis.client import Redis
from sqlalchemy.orm import Session

from schemas.familyfeud import GameRound, GameStatus, LiveGame, LiveGameType
from services.chat_service import read_user
from services.games.family import read_games_by_user, create_game_by_user, read_game, create_game_data, \
    set_game_status, read_game_by_code
from utils.auth import get_current_user
from utils.database import get_db
from utils.redis_database import get_redis
from utils.schemas import User

router = APIRouter(prefix="/api/familyfeud")
connected_clients = {}

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
    logger.info(f"{code} {data}")
    user_id = read_user(user, postgres_client)
    create_game_data(code, data, user_id, postgres_client)
    return read_game(code, user_id, postgres_client)


@router.post("/games/{code}/status")
async def start_game(
        code: str,
        game_status: GameStatus,
        user: User = Depends(get_current_user),
        redis_client: Redis = Depends(get_redis),
        postgres_client: Session = Depends(get_db)
):
    user_id = read_user(user, postgres_client)
    return await set_game_status(code, user_id, game_status, postgres_client, redis_client)


@router.websocket("/ws/{code}")
async def websocket_endpoint(
        code: str,
        websocket: WebSocket,
        auth: str | None = None,
        redis_client: Redis = Depends(get_redis),
        postgres_client: Session = Depends(get_db),
):
    await websocket.accept()

    # check if game exists
    game = read_game_by_code(code, postgres_client)
    if game is None:
        await websocket.send_text(LiveGame(
            type=LiveGameType.error,
            answers=[],
            number=-1,
            question="",
            strikes=-1
        ).model_dump_json())
        await websocket.close()
        return
    is_authenticated = game.auth == auth

    # update connections
    if code in connected_clients:
        connected_clients[code].append(websocket)
    else:
        connected_clients[code] = [websocket]

    # send current game state
    game_data = await redis_client.hget("games", code)
    if game_data:
        await websocket.send_text(game_data)
    else:
        logger.error(f"No game data: {code}")
        await websocket.send_text(LiveGame(
            type=LiveGameType.error,
            answers=[],
            number=-1,
            question="",
            strikes=-1
        ).model_dump_json())
        await websocket.close()
        return

    try:
        while True:
            live_game = LiveGame(**json.loads(await websocket.receive_text()))
            if is_authenticated:
                await redis_client.hset("games", code, live_game.model_dump_json())
                for client in connected_clients[code]:
                    try:
                        await client.send_text(live_game.model_dump_json())
                    except Exception as ee:
                        print(websocket, client, ee)
    except (ValidationError or ValueError) as ve:
        logger.error(ve)
        await websocket.close()
    except Exception as e:
        logger.error(e)
    finally:
        connected_clients[code].remove(websocket)

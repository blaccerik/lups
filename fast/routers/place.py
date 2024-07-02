import json
import logging
from typing import List

from fastapi import APIRouter, Depends, WebSocket
from pydantic import ValidationError
from redis.client import Redis

from services.place_service import update_pixel, read_pixels
from utils.auth import get_current_user_with_token
from database.redis_database import get_redis_database
from schemas.schemas import PlaceInput, PlaceOutput

router = APIRouter(prefix="/api/place", tags=["Place"])
connected_clients = []

logger = logging.getLogger("Place")


# response model must be set for faster send
@router.get("/", response_model=List[PlaceOutput])
async def get_pixels(redis_client: Redis = Depends(get_redis_database)):
    return await read_pixels(redis_client)


@router.websocket("/ws")
async def websocket_endpoint(authorization: str, websocket: WebSocket, redis_client: Redis = Depends(get_redis_database)):
    await websocket.accept()
    user = await get_current_user_with_token(authorization)
    # Add the websocket to the list of connected clients
    connected_clients.append(websocket)
    try:
        while True:
            place_input = PlaceInput(**json.loads(await websocket.receive_text()))
            place_input.validate_matrix_size(place_input.matrix, place_input.size)

            logger.info(f"{user} placed: {place_input.size * place_input.size}")

            # user not logged in
            if not user:
                continue

            # edit database
            place_outputs = await update_pixel(place_input, user, redis_client)
            # send message
            for client in connected_clients:
                await client.send_text(json.dumps(place_outputs))
    except (ValidationError or ValueError) as ve:
        logger.error(ve)
        await websocket.close()
    except Exception as e:
        logger.error(e)
    finally:
        # Remove the disconnected WebSocket from the list
        connected_clients.remove(websocket)

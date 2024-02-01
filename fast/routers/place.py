import json
import logging
from typing import List

from fastapi import APIRouter, Depends, WebSocket
from pydantic import ValidationError
from redis.client import Redis

from services.place_service import update_pixel, read_pixels_redis
from utils.auth import get_current_user_with_token
from utils.redis_database import get_redis
from utils.schemas import PixelSmall, PlaceInput

router = APIRouter(prefix="/api/place")
connected_clients = []

logger = logging.getLogger("Place")


@router.get("/", response_model=List[PixelSmall])
async def get_pixels(redis_client: Redis = Depends(get_redis)):
    return await read_pixels_redis(redis_client)


@router.websocket("/ws")
async def websocket_endpoint(authorization: str, websocket: WebSocket, redis_client: Redis = Depends(get_redis)):
    await websocket.accept()
    print(websocket)
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
            await update_pixel(place_input, redis_client)
            # for client in connected_clients:
            #     await client.send_text(json.dumps({
            #         "x": data["x"],
            #         "y": data["y"],
            #         "color": data["color"]
            #     }))
    except (ValidationError or ValueError) as ve:
        print("validation")
        print(ve)
        print("validation")
        await websocket.close()
    except Exception as e:
        print("error")
        print(e)
        print("error")
    finally:
        # Remove the disconnected WebSocket from the list
        connected_clients.remove(websocket)

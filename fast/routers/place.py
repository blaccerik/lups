import json
from typing import List

from fastapi import APIRouter, Depends, WebSocket
from redis.client import Redis

from services.place_service import update_pixel, read_pixels_redis
from utils.auth import get_current_user_with_token
from utils.redis_database import get_redis
from utils.schemas import PixelSmall

router = APIRouter(prefix="/api/place")
connected_clients = []


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
            data = json.loads(await websocket.receive_text())
            print(data)
            # user not logged in
            if not user:
                continue

            # edit database
            x = data["x"]
            y = data["y"]
            color = data["color"]
            await update_pixel(x, y, color, redis_client)
            for client in connected_clients:
                await client.send_text(json.dumps({
                    "x": data["x"],
                    "y": data["y"],
                    "color": data["color"]
                }))
    except Exception as e:
        print(e)
        pass
    finally:
        # Remove the disconnected WebSocket from the list
        connected_clients.remove(websocket)

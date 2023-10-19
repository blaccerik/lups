import asyncio
import json
import random

from fastapi import APIRouter, Depends, WebSocket
from redis.client import Redis

from services.place_service import COLORS
from utils.auth import get_current_user, get_current_user_with_token
from utils.redis_database import get_redis
from utils.schemas import User

router = APIRouter(prefix="/api/place")
connected_clients = []


@router.get("/")
async def get_chats(redis_client: Redis = Depends(get_redis)):
    print("test")
    pixels = await redis_client.hgetall("pixels")
    pixels = [{
        "x": int(p.split("_")[0]),
        "y": int(p.split("_")[1]),
        "c": int(pixels[p])
    } for p in pixels]
    return pixels


@router.websocket("/ws")
async def websocket_endpoint(authorization: str, websocket: WebSocket, redis_client: Redis = Depends(get_redis)):
    await websocket.accept()
    user = await get_current_user_with_token(authorization)
    # Add the websocket to the list of connected clients
    connected_clients.append(websocket)
    try:
        while True:
            data = json.loads(await websocket.receive_text())

            # edit database
            print(user)

            for client in connected_clients:
                await client.send_text(json.dumps({
                    "x": data["x"],
                    "y": data["y"],
                    "c": COLORS.index(data["color"])
                }))
    except Exception as e:
        print(e)
        pass
    finally:
        # Remove the disconnected WebSocket from the list
        connected_clients.remove(websocket)

async def send_dummy_message():
    while True:
        await asyncio.sleep(0.2)  # Wait for 1 second

        j = json.dumps({
            "c": random.randrange(0, 8),
            "x": random.randrange(0, 300),
            "y": random.randrange(0, 300)
        })
        # print(len(connected_clients))
        for client in connected_clients:
            await client.send_text(j)
loop = asyncio.get_event_loop()

loop.create_task(send_dummy_message())
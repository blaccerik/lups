from fastapi import APIRouter, Depends
from redis.client import Redis
from sqlalchemy.orm import Session

from services.place_service import read_pixels
from utils.database import get_db
from utils.redis_database import get_redis

router = APIRouter(prefix="/api/place")


@router.get("/")
async def get_chats(db: Session = Depends(get_db)):
    pixels = read_pixels(db)
    return pixels


@router.get("/hello")
async def get_chats(db: Redis = Depends(get_redis)):
    e = await db.get("erik")
    print(e)
    return "erik"

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             # edit_pixel()
#             print(data)
#             await websocket.send_text("{'hi': 2}")
#     except WebSocketDisconnect:
#         pass

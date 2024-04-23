import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import news, place, chat, familyfeud, music
from database.postgres_database import SessionLocal
from database.redis_database import get_client
from schemas.schemas import PlacePixel, PlaceColor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an instance of FastAPI
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=origins,
)

app.include_router(chat.router)
app.include_router(place.router)
app.include_router(news.router)
app.include_router(familyfeud.router)
app.include_router(music.router)

@app.get("/")
async def main():
    return "get works now"

@app.on_event("startup")
async def startup_event():
    # from models.models import init_db
    # init_db()

    redis_client = get_client()
    postgres_client = SessionLocal()
    # clear redis jobs
    print(await redis_client.hgetall("streams"))
    print(await redis_client.smembers("chats"))
    print(await redis_client.hgetall("games"))
    await redis_client.delete("streams")
    await redis_client.delete("chats")
    print(await redis_client.hgetall("streams"))
    print(await redis_client.smembers("chats"))

    # init place if needed
    pixels = await redis_client.hgetall("pixels")
    try:
        for pixel in pixels.values():
            PlacePixel(**json.loads(pixel))
        print("place data ok")
    except Exception as e:
        print(e)
        data = {}
        for x in range(300):
            for y in range(300):
                field_name = f"{x}_{y}"
                data[field_name] = PlacePixel(
                    color=PlaceColor.white.value,
                    user=None
                ).model_dump_json()
        await redis_client.hset('pixels', mapping=data)
        print("place data init")
    postgres_client.close()
    await redis_client.close()

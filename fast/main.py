import logging
import sys
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import items, websocket, news, place, chat
from services.place_service import read_pixels
from utils.database import SessionLocal
from utils.redis_database import get_client

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

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

app.include_router(items.router)
app.include_router(websocket.router)
app.include_router(chat.router)
app.include_router(place.router)
app.include_router(news.router)


@app.on_event("startup")
async def startup_event():
    redis_client = get_client()
    postgres_client = SessionLocal()
    t1 = time.time()
    old = await redis_client.hgetall("pixels")
    # todo dont keep this on for prod mode
    print(len(old))
    if len(old) != 90000:
        pixels = read_pixels(postgres_client)
        for pixel in pixels:
            field_name = f"{pixel['x']}_{pixel['y']}"
            await redis_client.hset('pixels', field_name, pixel['c'])
    t2 = time.time()
    print(t2 - t1)
    postgres_client.close()
    await redis_client.close()

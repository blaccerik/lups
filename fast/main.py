import logging
import sys

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
    e = await redis_client.get("erik")
    print(e)
    pixels = read_pixels(postgres_client)
    print(len(pixels))
    postgres_client.close()
    await redis_client.close()
    # with get_session() as session:
    #     pixels = read_pixels(session)
    #     for pixel in pixels:
    #         # Use the x and y coordinates as the field names in Redis
    #         field_name = f"{pixel.x}_{pixel.y}"
    #         # Store the pixel color as the field value
    #         redis_client.hset('pixels', field_name, pixel.color)

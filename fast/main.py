import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import news, place, chat, familyfeud
from utils.database import SessionLocal
from utils.redis_database import get_client
from utils.schemas import PlacePixel, PlaceColor

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

# app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(chat.router)
app.include_router(place.router)
app.include_router(news.router)
app.include_router(familyfeud.router)



@app.on_event("startup")
async def startup_event():
    # from models.models import init_db
    # init_db()

    redis_client = get_client()
    postgres_client = SessionLocal()
    # clear redis jobs
    print(await redis_client.hgetall("streams"))
    print(await redis_client.smembers("chats"))
    await redis_client.delete("streams")
    await redis_client.delete("chats")
    print(await redis_client.hgetall("streams"))
    print(await redis_client.smembers("chats"))
    # print(await redis_client.scan(_type="STREAM"))
    # async for i in redis_client.scan_iter(_type="STREAM"):
    #     await redis_client.delete(i)
    # print(await redis_client.scan(_type="STREAM"))
    # print(await redis_client.scan())
    # print(await redis_client.smembers("streams"))
    # await redis_client.delete("streams")
    # print(await redis_client.smembers("streams"))
    # if await redis_client.hexists("streams"):
    # print(await redis_client.xinfo_groups("streams"))
    # print(await redis_client.xinfo_stream("streams"))
    # print(await redis_client.hgetall("streams"))
    # await redis_client.delete("streams")
    # print(await redis_client.hgetall("streams"))
    # load pixels
    # try:
    #     t1 = time.time()
    #     # old = await redis_client.hgetall("pixels")
    #     # # todo dont keep this on for prod mode
    #     # if len(old) != 90000:
    #     #     pixels = read_pixels(postgres_client)
    #     #     pixel_data = {}
    #     #     for pixel in pixels:
    #     #         field_name = f"{pixel.x}_{pixel.y}"
    #     #         pixel_data[field_name] = pixel.color
    #     #     await redis_client.hmset('pixels', pixel_data)
    #     t2 = time.time()
    #     print("time taken", t2 - t1)
    # except Exception as e:
    #     logger.error(e)

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

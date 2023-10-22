from typing import List

from redis.client import Redis
from sqlalchemy.orm import Session

from models.models import DBPixel
from utils.schemas import Pixel

SIZE = 300
COLORS = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
]


def read_pixels(session: Session) -> List[Pixel]:
    pixels = session.query(DBPixel).all()
    return [Pixel(x=p.x, y=p.y, c=COLORS.index(p.color)) for p in pixels]


async def read_pixels_redis(redis_client: Redis) -> List[Pixel]:
    pixels = await redis_client.hgetall("pixels")
    return [Pixel(
        x=int(k.split("_")[0]),
        y=int(k.split("_")[1]),
        c=COLORS.index(v)
    ) for k, v in pixels.items()]


async def update_pixel(x, y, color, redis_client: Redis):
    if x < 0 or x >= SIZE:
        return False
    elif y < 0 or y >= SIZE:
        return False
    elif color not in COLORS:
        return False
    field_name = f"{x}_{y}"
    await redis_client.hset('pixels', field_name, color)
    return True

from typing import List

from redis.client import Redis
from sqlalchemy.orm import Session

from models.models import DBPixel
from utils.schemas import PixelSmall, PixelLarge, PlaceInput

SIZE = 300
COLORS = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
]


def read_pixels(session: Session) -> List[PixelLarge]:
    pixels = session.query(DBPixel).all()
    return [PixelLarge(x=p.x, y=p.y, color=p.color) for p in pixels]


async def read_pixels_redis(redis_client: Redis) -> List[PixelSmall]:
    pixels = await redis_client.hgetall("pixels")
    return [PixelSmall(
        x=int(k.split("_")[0]),
        y=int(k.split("_")[1]),
        c=COLORS.index(v)
    ) for k, v in pixels.items()]


async def update_pixel(place_input: PlaceInput, redis_client: Redis):
    delta = place_input.size // 2
    values = {}
    for i in range(place_input.size):
        for j in range(place_input.size):
            color = place_input.matrix[i][j]
            if not color:
                continue
            dx = place_input.x + i - delta
            dy = place_input.y + j - delta
            field_name = f"{dx}_{dy}"
            if 0 <= dx < SIZE and 0 <= dy < SIZE:
                values[field_name] = color.value
    await redis_client.hset('pixels', mapping=values)

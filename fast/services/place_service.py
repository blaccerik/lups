from redis.client import Redis
from sqlalchemy.orm import Session

from models.models import DBPixel

SIZE = 300
COLORS = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
]


def read_pixels(session: Session):
    pixels = session.query(DBPixel).all()
    return [{
        "x": p.x,
        "y": p.y,
        "c": COLORS.index(p.color)
    } for p in pixels]


async def edit_pixel(x, y, color, redis_client: Redis):
    if x < 0 or x >= SIZE:
        return False
    elif y < 0 or y >= SIZE:
        return False
    elif color not in COLORS:
        return False
    field_name = f"{x}_{y}"
    await redis_client.hset('pixels', field_name, color)
    return True

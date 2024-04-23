import json
from typing import List

from redis.client import Redis

from schemas.schemas import PlaceInput, User, PlacePixel, PlaceOutput

SIZE = 300
COLORS = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
]


async def read_pixels(redis_client: Redis) -> List[PlaceOutput]:
    pixels = await redis_client.hgetall("pixels")
    values = []
    for key, pixel in pixels.items():
        x = int(key.split("_")[0])
        y = int(key.split("_")[1])
        # values.append(key + ":" + pixel)
        data = json.loads(pixel)
        # keep it dict for faster load
        values.append({
            "u": data["user"],
            "c": data["color"],
            "x": x,
            "y": y
        })
    return values


async def update_pixel(place_input: PlaceInput, user: User, redis_client: Redis):
    delta = place_input.size // 2
    values = {}
    result = []
    for i in range(place_input.size):
        for j in range(place_input.size):
            color = place_input.matrix[i][j]
            if not color:
                continue
            dx = place_input.x + i - delta
            dy = place_input.y + j - delta
            field_name = f"{dx}_{dy}"
            if 0 <= dx < SIZE and 0 <= dy < SIZE:
                values[field_name] = PlacePixel(color=color.value, user=user.name).model_dump_json()
                result.append(PlaceOutput(
                    c=color.value,
                    u=user.name,
                    x=dx,
                    y=dy
                ).model_dump())
    await redis_client.hset('pixels', mapping=values)

    return result

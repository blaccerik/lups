import redis.asyncio as redis
import os

REDIS_HOST = os.environ.get('REDIS_HOST', "localhost")
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)


def get_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


async def get_redis():
    redis_instance = get_client()
    try:
        yield redis_instance
    finally:
        await redis_instance.aclose()

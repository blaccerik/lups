import os

import redis.asyncio as redis


def get_client():
    return redis.Redis(host=os.environ.get('REDIS_BROKER_URL', 'localhost'), port=6379, db=0, decode_responses=True)


async def get_redis_database():
    redis_instance = get_client()
    try:
        yield redis_instance
    finally:
        await redis_instance.aclose()

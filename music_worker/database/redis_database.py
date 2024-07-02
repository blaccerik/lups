import logging
import platform

from redis import Redis

logger = logging.getLogger(__name__)

operating_system = platform.system()
HOST = "redis"
if operating_system == 'Windows':
    HOST = "localhost"
logger.info(HOST)
REDIS_DATABASE_URI = f"redis://redis:6379/0"



def get_client() -> Redis:
    return Redis(host=HOST, port=6379, db=0)

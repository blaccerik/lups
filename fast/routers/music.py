import logging

from fastapi import APIRouter

router = APIRouter(prefix="/api/music")
logger = logging.getLogger("Music")


@router.get("/")
async def get_music(
):
    return "get works"
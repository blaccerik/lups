from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from services.news_service import read_all_news
from utils.database import get_db
from utils.schemas import News

router = APIRouter(prefix="/api/news")


@router.get("/", response_model=List[News])
async def get_news(page=0, db: Session = Depends(get_db)):
    return read_all_news(page, db)

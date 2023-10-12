from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from services.news_service import read_all_news
from utils.database import get_db

router = APIRouter(prefix="/api/news")

@router.get("/")
async def get_news(page: int, db: Session = Depends(get_db)):
    news = read_all_news(page, db)
    return news
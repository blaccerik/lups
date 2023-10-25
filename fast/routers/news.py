from typing import List

from fastapi import APIRouter, Form, UploadFile, File
from fastapi.params import Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from services.chat_service import read_user
from services.news_service import read_all_news, read_news, find_image, create_news
from utils.auth import get_current_user
from utils.database import get_db
from utils.schemas import News, NewsId, User

router = APIRouter(prefix="/api/news")


@router.get("/", response_model=List[News])
async def get_news(page: int = 0, db: Session = Depends(get_db)):
    return read_all_news(page, db)


@router.get("/{news_id}", response_model=News)
async def get_news_by_id(news_id: int, db: Session = Depends(get_db)):
    return read_news(news_id, db)


@router.get("/{news_id}/image", response_class=FileResponse)
async def get_news_image(news_id: int):
    image_path = find_image(news_id)
    return FileResponse(image_path)


@router.post("/create", response_model=NewsId)
async def post_news(
        title: str = Form(),
        text: str = Form(),
        category: str = Form(),
        image: UploadFile = File(default=None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_id = read_user(current_user, db)
    return create_news(user_id, title, text, category, image, db)


@router.put("/{news_id}", response_model=NewsId)
async def put_news(
        news_id: int,
        title: str = Form(),
        text: str = Form(),
        category: str = Form(),
        image: UploadFile = File(default=None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_id = read_user(current_user, db)
    return create_news(user_id, title, text, category, image, db, news_id)

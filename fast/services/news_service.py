import os
import sys
from pathlib import Path

from PIL import Image
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from models.models import DBNews, DBNewsCategory, DBUser, DBNewsExtra
from utils.schemas import News, NewsId

if sys.platform == "win32":
    IMAGE_PATH = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/images"
else:
    IMAGE_PATH = "/usr/src/app/images"

NEWS_PAGE_SIZE = 15
NEWS_CATEGORIES = [
    "Eesti",
    "Majandus",
    "Auto",
    "Tervis"
]


def db_news_to_news(n, include_text) -> News:
    date = n.date.strftime("%d.%m.%Y")
    gid = None
    if n.google_id:
        name = n.user_name
        gid = n.google_id
    else:
        name = n.creator
    news = News(
        creator_id=gid,
        creator=name,
        id=n.id,
        title=n.title,
        date=date,
        category=n.category_name,
        text="",
        has_image=os.path.exists(IMAGE_PATH + f"/{n.id}.jpg")
    )
    if include_text:
        news.text = n.text
    if n.link:
        news.link = n.link
    return news


def read_all_news(page_nr: int, session: Session):
    news = (session.query(
        DBNews.id,
        DBNews.title,
        DBNews.text,
        DBNews.date,
        DBNewsCategory.name.label('category_name'),
        DBUser.name.label('user_name'),
        DBUser.google_id,
        DBNewsExtra.link,
        DBNewsExtra.creator
    ).join(DBNewsCategory, DBNews.category_id == DBNewsCategory.id)
            .outerjoin(DBUser, DBNews.user_id == DBUser.id)
            .outerjoin(DBNewsExtra, DBNews.id == DBNewsExtra.id).order_by(DBNews.date.desc())
            .offset(page_nr * NEWS_PAGE_SIZE).limit(NEWS_PAGE_SIZE).all())
    return [db_news_to_news(n, include_text=False) for n in news]


def read_news(news_id: int, session: Session):
    news = (session.query(
        DBNews.id,
        DBNews.title,
        DBNews.text,
        DBNews.date,
        DBNewsCategory.name.label('category_name'),
        DBUser.name.label('user_name'),
        DBUser.google_id,
        DBNewsExtra.link,
        DBNewsExtra.creator
    ).join(DBNewsCategory, DBNews.category_id == DBNewsCategory.id)
            .outerjoin(DBUser, DBNews.user_id == DBUser.id)
            .outerjoin(DBNewsExtra, DBNews.id == DBNewsExtra.id)
            .filter(DBNews.id == news_id).first())
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return db_news_to_news(news, include_text=True)


def save_file(file, news_id: int):
    image = Image.open(file)

    # Convert the image to RGB mode
    image = image.convert('RGB')

    # Resize the image to 300x300 pixels
    resized_image = image.resize((300, 300))
    resized_image.save(IMAGE_PATH + f"/{news_id}.jpg")


def remove_file(news_id: int):
    if os.path.exists(IMAGE_PATH + f"/{news_id}.jpg"):
        os.remove(IMAGE_PATH + f"/{news_id}.jpg")


def find_image(news_id: int):
    # try to find image
    path = f"{IMAGE_PATH}/{news_id}.jpg"
    if os.path.exists(path):
        return path
    raise HTTPException(status_code=404, detail="Image not found")


def create_news(
        user_id: int,
        title: str,
        text: str,
        category: str,
        file: UploadFile,
        session: Session,
        news_id=None) -> NewsId:
    # check if can edit
    if news_id:
        n = session.query(DBNews).get(news_id)
        if n is None:
            raise HTTPException(status_code=404, detail="News not found")
        if n.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not news owner")
    else:
        n = DBNews()
    n.title = title
    n.text = text
    n.user_id = user_id

    # create category if needed
    category = category.lower()
    nc = session.query(DBNewsCategory).filter(DBNewsCategory.name == category).first()
    if nc is None:
        nc = DBNewsCategory()
        nc.name = category
        session.add(nc)
        session.flush()
    n.category_id = nc.id
    session.add(n)
    session.commit()
    if file:
        save_file(file.file, n.id)
    else:
        remove_file(n.id)
    return NewsId(id=n.id)

import os
import sys
from pathlib import Path

from PIL import Image
from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from models.models import DBNews, DBNewsCategory, DBUser
from utils.schemas import News

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
    news = News(
        creator_id=n.google_id,
        creator=n.name,
        id=n.id,
        title=n.title,
        date=date,
        category=n.cat_name,
        text="",
        has_image=os.path.exists(IMAGE_PATH + f"/{n.id}.jpg")
    )
    if include_text:
        news.text = n.text

    return news


def read_all_news(page_nr: int, session: Session):
    news = session.query(
        DBNews.id,
        DBNews.title,
        DBNews.date,
        DBNewsCategory.name.label("cat_name"),
        DBUser.name.label("user_name"),
        DBUser.google_id
    ).join(DBNewsCategory).join(DBUser).order_by(desc(DBNews.id)).offset(page_nr * NEWS_PAGE_SIZE).limit(
        NEWS_PAGE_SIZE).all()
    return [db_news_to_news(n, include_text=False) for n in news]


def read_news(news_id: int, session: Session):
    news = session.query(
        DBNews.id,
        DBNews.title,
        DBNews.date,
        DBNews.text,
        DBNewsCategory.name.label("cat_name"),
        DBUser.name.label("user_name"),
        DBUser.google_id
    ).join(DBNewsCategory).join(DBUser).filter(DBNews.id == news_id).first()
    print(news, news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return db_news_to_news(news, include_text=True)


# def create_news(
#         user_id: int,
#         title: str,
#         text: str,
#         category: str,
#         file,
#         news_id=None,
#         session=None) -> int:
#     # todo add right to create news
#
#     # check if can edit
#     if news_id:
#         n = session.query(News).get(news_id)
#         if n is None:
#             abort(404, "News not found")
#         if n.user_id != user_id:
#             abort(403, "User is not owner")
#     else:
#         n = News()
#     n.title = title
#     n.text = text
#     n.user_id = user_id
#
#     # create category if needed
#     category = category.lower()
#     nc = session.query(NewsCategory).filter(NewsCategory.name == category).first()
#     if nc is None:
#         nc = NewsCategory()
#         nc.name = category
#         session.add(nc)
#         session.commit()
#     n.category_id = nc.id
#     session.add(n)
#     session.commit()
#     if file:
#         save_file(file, n.id)
#     else:
#         remove_file(n.id)
#     return n.id

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

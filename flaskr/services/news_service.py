import os.path
import sys
from pathlib import Path

from PIL import Image
from flask import abort

from db_models.models import with_session, News, User, NewsCategory

# running locally
if sys.platform == "win32":
    IMAGE_PATH = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/images"
else:
    IMAGE_PATH = "/usr/src/app/images"

NEWS_PAGE_SIZE = 15

@with_session
def create_news(user_id: int, title: str, text: str, cat: str, session=None) -> int:

    # create cat if needed
    nc = session.query(NewsCategory).filter(NewsCategory.name == cat).first()
    if nc is None:
        nc = NewsCategory()
        nc.name = cat
        session.add(nc)
        session.commit()
    # todo add right to create news
    n = News()
    n.title = title
    n.text = text
    n.user_id = user_id
    n.category_id = nc.id
    session.add(n)
    session.commit()
    return n.id


def db_news_to_dict(n, include_text):
    date = n.date.strftime("%d.%m.%Y")
    news_dict = {
        "title": n.title,
        "date": date,
        "category": n.cat_name,
        "creator": n.user_name,
        "creator_id": n.google_id
    }
    if include_text:
        news_dict["text"] = n.text

    return news_dict


@with_session
def get_news(news_id: int, session=None):
    news = session.query(
        News.title,
        News.date,
        News.text,
        NewsCategory.name.label("cat_name"),
        User.name.label("user_name"),
        User.google_id
    ).join(NewsCategory).join(User).filter(News.id == news_id).first()
    print(news, news_id)
    if news is None:
        abort(404, "News not found")
    return db_news_to_dict(news, include_text=True)

@with_session
def get_news_many(page_nr, session=None):
    news = session.query(
        News.title,
        News.date,
        NewsCategory.name.label("cat_name"),
        User.name.label("user_name"),
        User.google_id
    ).join(NewsCategory).join(User).offset(page_nr).limit(NEWS_PAGE_SIZE).all()
    results = []
    for n in news:
        results.append(db_news_to_dict(n, include_text=False))
    return results

@with_session
def edit(news_id: int, user_id: int, title: str, text: str, cat: str, new_file: str, file, session=None):
    news = session.query(News).get(news_id)
    if news is None:
        abort(404, "News not found")
    if news.user_id != user_id:
        abort(403, "User is not owner")
    # create cat if needed
    nc = session.query(NewsCategory).filter(NewsCategory.name == cat).first()
    if nc is None:
        nc = NewsCategory()
        nc.name = cat
        session.add(nc)
        session.commit()
    news.title = title
    news.text = text
    news.category_id = nc.id
    if new_file:
        if file:
            save_file(file, news_id)
        else:
            if os.path.exists(IMAGE_PATH + f"/{news_id}.jpg"):
                os.remove(IMAGE_PATH + f"/{news_id}.jpg")
    session.add(news)
    session.commit()




def save_file(file, news_id: int):

    image = Image.open(file)

    # Convert the image to RGB mode
    image = image.convert('RGB')

    # Resize the image to 300x300 pixels
    resized_image = image.resize((300, 300))
    resized_image.save(IMAGE_PATH + f"/{news_id}.jpg")


def find_image(news_id: int):
    # try to find image
    path = f"{IMAGE_PATH}/{news_id}.jpg"
    if os.path.exists(path):
        return path
    abort(404, "Image not found")

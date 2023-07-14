import os.path
import sys
from pathlib import Path

from PIL import Image
from flask import abort

from db_models.models import with_session, News, User


# running locally
if sys.platform == "win32":
    IMAGE_PATH = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/images"
else:
    IMAGE_PATH = "/usr/src/app/images"


@with_session
def create_news(user_id: int, title: str, text: str, session=None) -> int:
    # todo add right to create news
    n = News()
    n.title = title
    n.text = text
    n.user_id = user_id
    session.add(n)
    session.commit()
    return n.id

@with_session
def get_news(news_id: int, session=None):
    news = session.query(News).get(news_id)
    if news is None:
        abort(404, "News not found")
    user = session.query(User).get(news.user_id)
    return {
        "title": news.title,
        "text": news.text,
        "creator": user.name,
        "creator_id": user.google_id
    }

@with_session
def edit(news_id: int, user_id: int, title: str, text: str, new_file: str, file, session=None):
    news = session.query(News).get(news_id)
    if news is None:
        abort(404, "News not found")
    if news.user_id != user_id:
        abort(403, "User is not owner")
    news.title = title
    news.text = text
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

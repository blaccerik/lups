import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from newsdataapi import NewsDataApiClient
from sqlalchemy.orm import Session

from worker.database import get_session, DBNews, DBNewsCategory, DBNewsExtra

if sys.platform == "win32":
    IMAGE_PATH = f"{Path(os.path.abspath(__file__)).parent.parent.parent}/images"
else:
    IMAGE_PATH = "/usr/src/app/images"

print(IMAGE_PATH)


def read_key():
    some_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    some_dir = os.path.join(some_dir, "key.txt")
    with open(some_dir, "r") as f:
        key = f.readline()
        return key


SOURCES = ["ohtuleht", "postimees", "telegramet", "saartehaal", "onlinele"]


def fetch_image_url(url, source):
    if source not in SOURCES:
        return None
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content, 'html.parser')

    # parse it by source
    if source == "ohtuleht":
        image_tag = soup.find("meta", {"property": "og:image"})
        if image_tag:
            image_url = image_tag.get("content")
            return image_url
    elif source == "postimees":
        image_tag = soup.find("meta", {"property": "og:image"})
        if image_tag:
            image_url = image_tag.get("content")
            return image_url
    elif source == "telegramet":
        image_tag = soup.find("meta", {"property": "og:image"})
        if image_tag:
            image_url = image_tag.get("content")
            return image_url
    elif source == "saartehaal":
        image_tag = soup.find("meta", {"property": "og:image"})
        if image_tag:
            image_url = image_tag.get("content")
            return image_url
    elif source == "onlinele":
        image_tag = soup.find("meta", {"property": "og:image"})
        if image_tag:
            image_url = image_tag.get("content")
            return image_url
    return None


def fetch_image(url, news_id):
    res = requests.get(url)
    if res.status_code != 200:
        return
    with open(f"{IMAGE_PATH}/{news_id}.jpg", "wb") as file:
        file.write(res.content)


def cat_to_est(string):
    translate = {
        "top": "top",
        "business": "äri",
        "world": "maailm",
        "sports": "sport",
        "entertainment": "meelelahutus",
        "health": "tervis",
        "food": "toit"
    }
    if string in translate:
        return translate[string]
    print(f"missing translate {string}")
    return "muu"


def process_news(result, session: Session):
    # dont add duplicates
    article_id = result["article_id"]
    existing_news = session.query(DBNewsExtra).filter_by(article_id=article_id).first()
    if existing_news:
        print(f"exists {article_id}")
        return

    dbnews = DBNews()
    dbnews.title = result["title"]
    date = result["pubDate"]
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
    # date = date.strftime("%d.%m.%Y")
    dbnews.date = date

    content = result["content"]
    desc = result["description"]
    if content and not desc:
        dbnews.text = content
    elif desc and not content:
        dbnews.text = desc
    elif content and desc:
        if len(content) > len(desc):
            dbnews.text = content
        else:
            dbnews.text = desc
    else:
        print("No data")
        return

    category = result["category"][0]
    # keywords = result["keywords"]
    # if keywords:
    #     category_name = keywords[0]
    # else:
    category_name = cat_to_est(category)

    # get category
    existing_category = session.query(DBNewsCategory).filter_by(name=category_name).first()

    if existing_category:
        cat_id = existing_category.id
    else:
        print(f"category not found: {category_name}")
        return

    dbnews.category_id = cat_id
    session.add(dbnews)
    session.flush()

    dbextra = DBNewsExtra()
    dbextra.id = dbnews.id
    dbextra.link = result["link"]

    source = result["source_id"]
    creator = result["creator"]
    if creator:
        dbextra.creator = creator[0]
    else:
        dbextra.creator = source
    dbextra.article_id = result["article_id"]

    image_url = result["image_url"]
    link = result["link"]
    dbextra.link = link
    if image_url is None:
        image_url = fetch_image_url(link, source)
    if image_url:
        fetch_image(image_url, dbnews.id)
    session.add(dbextra)


def get_news():
    key = read_key()

    api = NewsDataApiClient(apikey=key)
    page = None
    with get_session() as session:
        while True:
            response = api.news_api(page=page, language="et")
            for res in response.get("results", []):
                process_news(res, session)
            session.commit()

            page = response.get('nextPage', None)
            s = response.get("status", None)
            tr = response.get("totalResults", None)
            print(f"{page} {s} {tr}")
            if not page:
                break
            time.sleep(1)

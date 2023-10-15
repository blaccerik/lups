import json
import os
import time
import uuid
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from newsdataapi import NewsDataApiClient


def read_key():
    with open("key.txt", "r") as f:
        key = f.readline()
        return key


def save_news(api_results):
    u = uuid.uuid4()
    with open(f"test/{u}.json", "w", encoding="utf-8") as file:
        json.dump(api_results, file, ensure_ascii=False, indent=4)


def main(key):
    api = NewsDataApiClient(apikey=key)
    page = None
    while True:
        response = api.news_api(page=page, language="et")
        save_news(response)
        page = response.get('nextPage', None)
        s = response.get("status", None)
        tr = response.get("totalResults", None)
        print(page, s, tr)
        if not page:
            break
        time.sleep(1)


def read_news():
    for i in os.listdir("test"):
        with open(f"test/{i}", "r", encoding="utf-8") as file:
            data = json.load(file)
            for res in data.get("results", []):
                news_id = process_news(res)


def process_news(result):
    title = result["title"]
    link = result["link"]
    date = result["pubDate"]
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
    date = date.strftime("%d.%m.%Y")

    source = result["source_id"]
    creator = result["creator"]

    content = result["content"]
    desc = result["description"]

    category = result["category"]
    keywords = result["keywords"]

    image_url = result["image_url"]
    id = result["article_id"]
    # if image_url is None:
    #     image_url = fetch_image_url(link, source)
    # if image_url:
    #     fetch_image(image_url)
    return id


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


def fetch_image(url):
    res = requests.get(url)
    if res.status_code != 200:
        return
    with open("image.jpg", "wb") as file:
        file.write(res.content)


if __name__ == '__main__':
    key = read_key()
    main(key)
    # read_news()

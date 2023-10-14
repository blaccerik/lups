import json
import os
import time

from newsdataapi import NewsDataApiClient

import uuid

def read_key():
    with open("key.txt", "r") as f:
        key = f.readline()
        return key

def save_news(api_results):
    u = uuid.uuid4()
    with open(f"test/{u}.json", "w", encoding="utf-8") as file:
        json.dump(api_results, file, ensure_ascii=False, indent=4)

def read_news():
    for i in os.listdir("test"):
        with open(f"test/{i}", "r", encoding="utf-8") as file:
            data = json.load(file)
            print(data.get("nextPage"), i)
        # break
        # print(i)
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

if __name__ == '__main__':
    # key = read_key()
    # main(key)
    read_news()
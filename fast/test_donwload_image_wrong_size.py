from io import BytesIO

import requests
from PIL import Image

# from utils.celery_config import celery_app

if __name__ == '__main__':

    # print("start")
    # s = celery_app.send_task("download_song_image", args=[
    #     "222",
    #     "https://i.ytimg.com/vi/cD4hxKkqR4E/hq720.jpg?sqp=-oaymwEXCNUGEOADIAQqCwjVARCqCBh4INgESFo&rs=AMzJL3mfA9ELHkm4qLqpjc-bRCUb00YrBA"
    # ], queue="music:1")
    # print(s)

    good_image_link = "https://lh3.googleusercontent.com/KIVnvVjBgHGZujevLRjZs2WOwLTtnbxFag3ACziFMwcL6z5FR2aYNW9PNBzBgxWd6kIVVtzavrQ44RM-=w544-h544-l90-rj"

    res = requests.get(good_image_link)

    image_link = "https://i.ytimg.com/vi/cD4hxKkqR4E/hq720.jpg?sqp=-oaymwEXCNUGEOADIAQqCwjVARCqCBh4INgESFo&rs=AMzJL3mfA9ELHkm4qLqpjc-bRCUb00YrBA"


    img = Image.open(BytesIO(res.content))
    w = img.width
    h = img.height
    if w != h:
        s = min(w, h)
        img = img.crop((
            (w - s) // 2,
            (h - s) // 2,
            w - ((w - s) // 2),
            h - ((h - s) // 2)
        ))
    img.save("test.jpg")

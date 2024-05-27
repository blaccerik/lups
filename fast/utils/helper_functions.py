import json

import requests

from database.models import DBFilter
from schemas.music_schema import Filter, FilterConfig


def dbfilter_to_filter(dbf: DBFilter | None) -> Filter:
    if dbf is None:
        return Filter(
            id=-1,
            name="None",
            config=[]
        )
    config_list = json.loads(dbf.config)
    return Filter(
        id=dbf.id,
        name=dbf.name,
        config=[FilterConfig(**c) for c in config_list]
    )


def _is_song_id_valid(song_id: str):
    print("API CALL")
    # hack by https://gist.github.com/tonY1883/a3b85925081688de569b779b4657439b
    url = f"https://img.youtube.com/vi/{song_id}/mqdefault.jpg"
    response = requests.head(url, allow_redirects=True, timeout=3)
    return response.status_code == 200

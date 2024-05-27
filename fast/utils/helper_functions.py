import json

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
